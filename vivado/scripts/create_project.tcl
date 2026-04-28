# set project_name [lindex $argv 0]
# set project_dir  [lindex $argv 1]

# create_project $project_name $project_dir/$project_name -part xc7z020clg400-1

# set_property top top [current_fileset]

# close_project

if {$tcl_platform(os) eq "Windows NT"} {
    set vivado_version [version -short]
    set board_repo_path "$env(APPDATA)/Xilinx/Vivado/$vivado_version/xhub/board_store/xilinx_board_store/XilinxBoardStore/Vivado/$vivado_version/boards/Digilent"
    set_param board.repoPaths $board_repo_path
}

set project_name [lindex $argv 0]
set project_dir  [lindex $argv 1]

create_project $project_name $project_dir/$project_name -part xc7z020clg400-1

set_property board_part digilentinc.com:zybo-z7-20:part0:1.2 [current_project]

set_property top top [current_fileset]

close_project