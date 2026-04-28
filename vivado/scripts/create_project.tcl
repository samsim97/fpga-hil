set project_name [lindex $argv 0]
set project_dir  [lindex $argv 1]

create_project $project_name $project_dir/$project_name -part xc7z020clg400-1

set_property top top [current_fileset]

close_project