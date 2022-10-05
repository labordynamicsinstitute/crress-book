# A script to install R dependencies for the github action.

pkg_list <- c("rmarkdown")

for (pkg in pkg_list) {  
  install.packages(pkg, repos = "your_cran_mirror", 
                   lib = "R/x86_64-pc-linux-gnu-library/3.3") 
  if (!require(pkg, character.only = T)) {
    quit(save = "no", status = 1, runLast = FALSE)  
  }
}
