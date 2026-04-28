set project_name [lindex $argv 0]
set project_dir  [lindex $argv 1]
set hdl_dir      [lindex $argv 2]

open_project $project_dir/$project_name/$project_name.xpr

add_files $hdl_dir

update_compile_order -fileset sources_1

close_project