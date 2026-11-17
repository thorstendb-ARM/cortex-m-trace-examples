# SPDX-License-Identifier: Apache-2.0
# Apply the documented CPU0-only override to the generated run description.
# Ruby's standard YAML library is the only dependency; no board access occurs.
require 'yaml'

root = File.expand_path('../..', __dir__)
path = File.join(root, 'out/Trace+EK-RA8P1.cbuild-run.yml')
abort 'Usage: ruby Board/EK-RA8P1/prepare_trace.rb [path/to/pyTS]' if ARGV.length > 1
if ARGV.empty?
  environment_path = File.join(root, '.cmsis/tools-environment.yml')
  abort 'Missing .cmsis/tools-environment.yml; refresh CMSIS Solution first' unless File.file?(environment_path)
  environment = YAML.safe_load(File.read(environment_path)).fetch('cmsis-tools-environment')
  debugger = environment.fetch('tools').find { |tool| tool['name'] == 'pyOCD' }
  abort 'CMSIS Debugger pyOCD tool not found in the selected environment' unless debugger
  directory = File.expand_path('../pyts', debugger.fetch('directory'))
  candidates = %w[pyTS pyTS.exe].map { |name| File.join(directory, name) }
  pyts = candidates.find { |candidate| File.file?(candidate) && File.executable?(candidate) }
  abort 'Bundled pyTS not found; pass its executable path explicitly' unless pyts
else
  pyts = File.expand_path(ARGV[0])
end
abort 'pyTS executable not found' unless File.file?(pyts) && File.executable?(pyts)

def require_value(condition, message)
  abort "RA8P1 trace setup: #{message}" unless condition
end

# Retain csolution's indentation for image entries. Some build-artifact
# consumers scan these entries line by line instead of parsing the YAML.
def write_yaml(path, document)
  # Use literal blocks for sequence code. Psych otherwise emits some
  # multiline strings as single quotes ending at column zero, which the
  # CMSIS Solution YAML reader rejects.
  syntax = Psych.parse_stream(YAML.dump(document))
  literal_strings = lambda do |node|
    if node.is_a?(Psych::Nodes::Scalar) && node.value.include?("\n")
      node.style = Psych::Nodes::Scalar::LITERAL
    end
    Array(node.children).each { |child| literal_strings.call(child) }
  end
  literal_strings.call(syntax)
  text = syntax.yaml
  if document.key?('cbuild-run')
    text.sub!(/(^  output:\n)(.*?)(?=^  [a-z])/m) do
      Regexp.last_match(1) + Regexp.last_match(2).lines.map { |line| '  ' + line }.join
    end
  end
  require_value(YAML.safe_load(text) == document, 'YAML round-trip mismatch')
  temporary = "#{path}.ra8p1-tmp"
  File.write(temporary, text)
  File.rename(temporary, path)
end

begin
  document = YAML.safe_load(File.read(path))
  run = document.fetch('cbuild-run')
  expected = {
    'target-type' => 'EK-RA8P1', 'target-set' => 'ULINKplus',
    'device' => 'Renesas::R7KA8P1KF', 'device-pack' => 'Renesas::RA_DFP@6.6.0'
  }
  expected.each { |key, value| require_value(run[key] == value, "unexpected #{key}; rebuild EK-RA8P1@ULINKplus") }
  require_value(run.fetch('output').all? { |image| image['pname'] == 'CPU0' }, 'expected CPU0 images only')
  debugger = run.fetch('debugger')
  require_value(debugger['name'] == 'ULINKplus@pyOCD', 'unexpected debugger')
  swo = debugger.fetch('trace').fetch(0)
  require_value(swo.key?('swo-uart') && swo['input-clock'] == 1_000_000 && swo['output-clock'] == 1_000_000,
                'expected 1 MHz trace input and 1 Mbaud SWO')

  override = YAML.safe_load(File.read(File.join(__dir__, 'trace-override.yml')))
  sequences = run['debug-sequences']
  require_value(sequences.nil? || sequences == override['debug-sequences'],
                'unexpected debug sequences; review instead of overwriting them')
  require_value(!run.key?('debug-sequences-conf'), 'expected legacy trace setup')
  topology = run.fetch('debug-topology')
  require_value(topology == { 'trace-sinks' => [{ 'serialwire' => nil }, { 'tracebuffer' => nil }] } ||
                topology == override['debug-topology'], 'unexpected debug topology')

  resources = run.fetch('system-resources')
  processors = resources.fetch('processors')
  require_value(processors.map { |p| p['pname'] }.sort == %w[CPU0 CPU1] ||
                processors.map { |p| p['pname'] } == ['CPU0'], 'unexpected processors')
  # This run describes the selected CPU0 image. CPU1/AP2 is not available in
  # the reference setup; pyTS must not emit disable writes for that processor.
  resources['processors'] = processors.select { |p| p['pname'] == 'CPU0' }
  resources['memory'].reject! { |m| m['pname'] == 'CPU1' }
  debugger['gdbserver'] = debugger.fetch('gdbserver').select { |server| [nil, 'CPU0'].include?(server['pname']) }
  debugger['gdbserver'].each { |server| server['pname'] = 'CPU0' }
  override.each { |key, value| run[key] = value }

  # Keep the filename and directory so relative ELF/profile paths stay valid.
  # Atomic replacement also avoids leaving a partial run description on failure.
  write_yaml(path, document)

  source_path = File.join(root, '.cmsis/Trace+EK-RA8P1@ULINKplus.ctrace.yml')
  source = YAML.safe_load(File.read(source_path))
  setup = source.fetch('ctrace').fetch('setup')
  require_value(setup.select { |entry| entry['pname'] == 'CPU1' }.all? { |entry| entry.key?('disable') },
                'refusing to remove an enabled CPU1 source profile')
  if setup.any? { |entry| entry['pname'] == 'CPU1' }
    setup.reject! { |entry| entry['pname'] == 'CPU1' }
    write_yaml(source_path, source)
  end
  abort 'pyTS generation failed' unless system(pyts, path, '--format', 'json')

  runtime_path = File.join(root, '.trace/Trace+EK-RA8P1@ULINKplus.ctrace-run.yml')
  runtime = YAML.safe_load(File.read(runtime_path))
  trace = runtime.fetch('ctrace-run')
  cpu1 = trace.fetch('ctrace-setup').select { |entry| entry['pname'] == 'CPU1' }
  require_value(cpu1.all? { |entry| entry.key?('disable') }, 'refusing to remove an enabled CPU1 source')
  require_value(trace.fetch('ctrace-refs').all? { |entry| [nil, 'CPU0'].include?(entry['pname']) && entry.fetch('ref').start_with?('CPU0/') },
                'expected CPU0 trace sources only')
  # Older generated source profiles may retain inactive CPU1 settings.
  # Omit only disable accesses; enabled CPU1 sources were rejected above.
  %w[ctrace-setup ctrace-disable].each do |key|
    trace.fetch(key).reject! { |entry| entry['pname'] == 'CPU1' }
  end
  require_value(trace.fetch('ctrace-setup').map { |entry| entry['pname'] } == ['CPU0'],
                'unexpected trace processors')
  write_yaml(runtime_path, runtime)
  puts 'Prepared CPU0/AP0 SWO and generated the trace runtime without CPU1 accesses.'
rescue KeyError, TypeError, NoMethodError, Psych::Exception, SystemCallError => error
  abort "RA8P1 trace setup: #{error.message}"
end
