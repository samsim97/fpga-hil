set project_name [lindex $argv 0]
set project_dir  [lindex $argv 1]
set xsa_path     [lindex $argv 2]

open_project $project_dir/$project_name/$project_name.xpr

# Standard default flow: synthesis through bitstream generation.
# If non-default strategies/options are ever needed (out-of-context synthesis,
# specific implementation strategies, etc.), add them here - confirm with the
# project owner before changing this, per the project's "no assumptions" rule.
launch_runs synth_1
wait_on_run synth_1

launch_runs impl_1 -to_step write_bitstream
wait_on_run impl_1

open_run impl_1

# Syntax confirmed against AMD UG835 (write_hw_platform Tcl command reference) and
# an official KV260 platform-creation tutorial:
#   write_hw_platform -include_bit -force -file <path>.xsa
write_hw_platform -include_bit -force -file $xsa_path

close_project
