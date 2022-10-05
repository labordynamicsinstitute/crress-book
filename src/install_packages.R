# A script to install R dependencies for the github action.

pkg_list <- c("rmarkdown")

for (pkg in pkg_list) {  
  install.packages(pkg, repos = "https://cloud.r-project.org/") 
  if (!require(pkg, character.only = T)) {
    quit(save = "no", status = 1, runLast = FALSE)  
  }
}
