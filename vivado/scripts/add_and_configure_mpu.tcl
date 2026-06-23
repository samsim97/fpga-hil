set project_name [lindex $argv 0]
set project_dir  [lindex $argv 1]
set xsa_path     [lindex $argv 2]

# Example path: C:\Users\Samuel\Documents\GitHub\fpga-hil\vivado\hil\hil
open_project $project_dir/$project_name/$project_name.xpr

# Create ze design with name (no shit tbk)
create_bd_design "system"
 
# Maybe useful or not, appeared after I created the design
update_compile_order -fileset sources_1
 
# Add the Zynq PS
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:processing_system7:5.5 processing_system7_0
endgroup
 
# Run automation for Zynq
apply_bd_automation -rule xilinx.com:bd_rule:processing_system7 -config {make_external "FIXED_IO, DDR" apply_board_preset "1" Master "Disable" Slave "Disable" }  [get_bd_cells processing_system7_0]
 
# Connect FCLK_CLK0 to M_AXI_GP0_ACLK on the Zynq
connect_bd_net [get_bd_pins processing_system7_0/FCLK_CLK0] [get_bd_pins processing_system7_0/M_AXI_GP0_ACLK]
 
# Enable the timers in the APU (Required for Ethernet)
startgroup
set_property -dict [list \
  CONFIG.PCW_QSPI_GRP_SINGLE_SS_ENABLE {1} \
  CONFIG.PCW_TTC0_PERIPHERAL_ENABLE {1} \
  CONFIG.PCW_TTC1_PERIPHERAL_ENABLE {1} \
] [get_bd_cells processing_system7_0]
endgroup

# Validating this after give some critical warnings, but forcing it again to validate don't show these critical warning. Is it useful to validate it 2 times?
validate_bd_design
# validate_bd_design -force
 
# Create the HDL Wrapper
make_wrapper -files [get_files $project_dir/$project_name/hil.srcs/sources_1/bd/system/system.bd] -top
 
add_files -norecurse $project_dir/$project_name/hil.gen/sources_1/bd/system/hdl/system_wrapper.v
 
# Set the top module to the system_wrapper
set_property top system_wrapper [current_fileset]
 
# Generate the Block Design
set_property synth_checkpoint_mode None [get_files  $project_dir/$project_name/hil.srcs/sources_1/bd/system/system.bd]
generate_target all [get_files  $project_dir/$project_name/hil.srcs/sources_1/bd/system/system.bd]
 
export_ip_user_files -of_objects [get_files $project_dir/$project_name/hil.srcs/sources_1/bd/system/system.bd] -no_script -sync -force -quiet
export_simulation \
    -lib_map_path [list \
        "modelsim=$project_dir/$project_name/hil.cache/compile_simlib/modelsim" \
        "questa=$project_dir/$project_name/hil.cache/compile_simlib/questa" \
        "riviera=$project_dir/$project_name/hil.cache/compile_simlib/riviera" \
        "activehdl=$project_dir/$project_name/hil.cache/compile_simlib/activehdl" \
    ] \
    -of_objects [get_files $project_dir/$project_name/hil.srcs/sources_1/bd/system/system.bd] \
    -directory $project_dir/$project_name/hil.ip_user_files/sim_scripts \
    -ip_user_files_dir $project_dir/$project_name/hil.ip_user_files \
    -ipstatic_source_dir $project_dir/$project_name/hil.ip_user_files/ipstatic \
    -use_ip_compiled_libs -force -quiet
 
# Export Hardware (Pre-synthesis)
write_hw_platform -fixed -force -file $project_dir/$project_name/system_wrapper.xsa