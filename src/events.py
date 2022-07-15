from data import Event, Paper
from pathlib import Path
import os
import re

root: Path = Path('crress/works')
converted_folder: Path = Path('converted')

latex_ignore = [
    ".fdb_latexmk",
    '.gz',
    '.pdf',
    '.fls',
    '.log',
    '.aux'
]

main_file_dict = {
    
}

def get_events():
    
    event_list = []
    
    for directory in root.glob("[!.]*"): # Don't include hidden files
        papers = []
        for paper_folder in directory.glob("[!.][!converted]*"):
            
            # try the dict first
            main_file = main_file_dict.get(directory.name)
            if main_file is not None:
                main_file = main_file_dict.get(directory.name).get(paper_folder.name)

            if main_file is None:
                non_dir = [x for x in paper_folder.glob("[!.]*") if not x.is_dir() and not x.suffix in latex_ignore]
                if len(non_dir) == 1:
                    print(f"assuming that main file for {paper_folder} in {directory} is {non_dir[0].name}")
                    main_file = non_dir[0]
                else:
                    raise Exception("Can't find main file")
                
            papers.append(
                Paper(
                    name=paper_folder.name,
                    main_file=main_file,
                )
            )
            
        event_list.append(Event(
            name=directory.name,
            papers = papers,
            path = directory
        ))
    return event_list

if __name__ == '__main__':

    get_events()

