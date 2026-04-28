set project_name  [lindex $argv 0]
set project_dir   [lindex $argv 1]
set constraints_dir [lindex $argv 2]

open_project $project_dir/$project_name/$project_name.xpr

add_files -fileset constrs_1 $constraints_dir

close_project