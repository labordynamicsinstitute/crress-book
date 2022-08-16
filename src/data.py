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
    

@dataclass
class Event:
    """Dataclass for an event
    """
    name: str
    papers: List[Paper]
    path: Path
    
    
    def n_papers(self):
        return len(self.papers)
        
    

    
    

            