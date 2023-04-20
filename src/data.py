import os
from pathlib import Path
from dataclasses import dataclass
from typing import List



@dataclass
class Paper:
    """Dataclass for a paper
    """
    name: str
    path: Path
    converted_path: Path
    main_file: Path
    
    def extension(self):
        return self.main_file.suffix.replace(".", '')
    
    def index_name(self):
        return (self.converted_path / self.main_file.name).with_stem("index")

    
    def rename_to_index(self):
        copied_path = self.converted_path / self.main_file.name
        copied_path.rename(self.index_name())
    

@dataclass
class Event:
    """Dataclass for an event
    """
    name: str
    papers: List[Paper]
    path: Path
    
    
    def n_papers(self):
        return len(self.papers)
        
    

    
    

            