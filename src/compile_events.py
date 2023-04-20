from data import Event, Paper
from pathlib import Path
import pypandoc
import shutil
import jupytext
import bibtexparser
from typing import Tuple
import frontmatter
import yaml
import requests
import io

from extra_authors import extra_authors

root: Path = Path('raw_writeups/')
converted_root: Path = Path("crress/sessions/")

CRRESS_WEBSITE_CONFIG = "https://raw.githubusercontent.com/labordynamicsinstitute/crress/main/_config.yml"


latex_ignore = [
    '.fdb_latexmk',
    '.gz',
    '.pdf',
    '.fls',
    '.log',
    '.aux',
    '.out'
]

other_ignore = [
    '.bib'
]

main_file_dict = {
    
}

def glob_multiple(path: Path, extensions: Tuple[str]):
    all_files = []
    for ext in extensions:
        all_files.extend(Path(path).glob(ext))
    return all_files

def get_events():
    
    event_list = []
    
    for directory in root.glob("[!.]*"): # Don't include hidden files
        papers = []
        # further filter the paper folder to get rid of converted folder and intro file
        directory_glob = [path for path in directory.glob("[!.]*")]
        for paper_folder in directory_glob:

            # try the dict first
            main_file = main_file_dict.get(directory.name)
            if main_file is not None:
                main_file = main_file_dict.get(directory.name).get(paper_folder.name)

            if main_file is None:
                non_dir = [x for x in paper_folder.glob("[!.]*") \
                    if not x.is_dir() \
                        and not x.suffix in latex_ignore \
                            and not x.suffix in other_ignore]
                if len(non_dir) == 1:
                    print(f"assuming that main file for {paper_folder} in {directory} is {non_dir[0].name}")
                    main_file = non_dir[0]
                elif len(non_dir) > 1:
                    print("More than one file in the directory. Choosing file with same name as parent")
                    for i in non_dir:
                        if i.stem == i.parent.stem:
                            main_file = i
                else:
                    raise Exception("Can't find main file")
                
            # now find references
            ref = [x for x in paper_folder.glob("[!.]*") \
                    if not x.is_dir() \
                        and x.suffix in ['.bib']]
            if len(ref) == 0:
                ref = None 
                
            papers.append(
                Paper(
                    name=paper_folder.name,
                    path=paper_folder,
                    converted_path=converted_root / paper_folder.parent.name / paper_folder.name,
                    main_file=main_file
                )
            )
            
        event_list.append(Event(
            name=directory.name,
            papers = papers,
            path = directory
        ))
    return event_list

def pandoc_convert(paper: Paper, fmt : str=None, **kwargs):
    if fmt is None:
        fmt=paper.extension()
    new_main_file_path = paper.index_name()
    return pypandoc.convert_file(str(new_main_file_path), 
                                 'markdown+yaml_metadata_block', 
                                 outputfile=str(new_main_file_path.with_suffix('.qmd')),
                                 **kwargs
                                 )
    
def jupytext_convert(paper: Paper, fmt: str=None):
    if fmt is None:
        fmt = paper.extension()
    new_main_file_path = paper.index_name()
    
    notebook = jupytext.read(str(new_main_file_path))
    
    return jupytext.write(notebook, str(new_main_file_path.with_suffix('.qmd')), fmt='qmd')

def parse_bibtex(paper: Paper):
    # Get bib files from converted path
    bibs = glob_multiple(paper.converted_path, ("*.bib", '*.bibtex'))
    
    if bibs:
        if len(bibs) > 1:
            raise Exception("Found more than one bib file, please check...")
        print(f"Found {bibs} bib file!")
        bib = bibs[0]
    
        return bibtexparser.loads(bib.read_text())
    else:
        print(f"No bib found in {paper.path}")
        return 

def get_panelist(panelist_list, key):
    for d in panelist_list:
        if d['tag'] == key:
            return d

    

if __name__ == '__main__':

    events = get_events()
    
    for event in events:
        for paper in event.papers:
            # create new directory for converted files
            shutil.copytree(paper.path, paper.converted_path, dirs_exist_ok=True)
            paper.rename_to_index()
            
            # Handle conversion
            if paper.extension().lower() in ['qmd', 'rmd']:
                continue
            elif paper.extension().lower() in ['ipynb'] :
                jupytext_convert(paper, fmt='qmd')
            elif paper.extension().lower() in ['docx']:
                pandoc_convert(paper, fmt='markdown+yaml_metadata_block', 
                               extra_args=[f'--extract-media={paper.converted_path}', 
                                           '--citeproc', 
                                           '--reference-doc=src/custom-reference.docx',
                                           '--standalone'])
            elif paper.extension().lower() in ['tex']:
                pandoc_convert(paper, fmt='markdown+yaml_metadata_block', 
                               extra_args=[f'--extract-media={paper.converted_path}', 
                                           '--citeproc', 
                                           '--reference-doc=src/custom-reference.docx',
                                           '--standalone',
                                           '--shift-heading-level-by=1'])
            else:
                pandoc_convert(paper, fmt='markdown+yaml_metadata_block', 
                               extra_args=['--citeproc'])
                
            # Now handle the bibtex parsing
            bib_parsed = parse_bibtex(paper)
            
            fname = paper.index_name().with_suffix(".qmd")
            
            # If media folder exists, then change media paths in qmd files to relative paths
            if (paper.converted_path / 'media/').is_dir():
                print(f"found media folder in {paper.converted_path}")
                
                
                f = open(fname, 'r')
                contents = f.readlines()
                f.close()
                
                for i, line in enumerate(contents):
                    if str(paper.converted_path) + '/' in line:
                        contents[i] = line.replace(str(paper.converted_path) + '/', '')
                        
                with open((paper.converted_path / paper.name).with_suffix(".qmd"), 'w') as f:
                    f.writelines(contents)
                        
            # add affiliations to paper based on _config.yml

            # load config from github:
            site_config = requests.get(CRRESS_WEBSITE_CONFIG).text.replace("\t", "") # sanitize or else PyYAML doesn't load it
            
            crress_panelists = yaml.safe_load(site_config)['panelists']
            
            # get part of dict for that panelist
            panelist_dict = get_panelist(crress_panelists, paper.name)
            
            with io.open(fname, 'r', encoding="utf-8-sig") as f:
                print(f"Added affiliation for {paper.name}, affil: {panelist_dict['affiliation']}")
                post = frontmatter.load(f)
                
                if not isinstance(post['author'], str) and len(post['author']) > 1:
                    print("found more than one author")
                    # get extra author affiliation
                    tag = paper.main_file.parent.stem
                    session = paper.main_file.parent.parent.stem
                    if extra_authors.get(session) is not None:
                        if extra_authors[session].get(tag) is not None:
                            e_a = extra_authors[session][tag]
                        else:
                            print("couldn't find session for extra author")
                    panelist_dict['affiliation'] = {
                        panelist_dict['name'] : panelist_dict['affiliation'],
                        e_a['name'] : e_a['affiliation']
                    }
                    
                    panelist_dict['affiliation'] = list(panelist_dict['affiliation'].values())

                if isinstance(post['author'], str) or (isinstance(post['author'], list) and len(post['author'])==1):
                    post['author'] = [post['author']]
                    panelist_dict['affiliation'] = [panelist_dict['affiliation']]
                    
                post['author'] = [{'name' : v } for v in post['author']]
                
                for d, p in zip(post['author'], panelist_dict['affiliation']):
                    d.update({'affiliations' : p})
                newfile = io.open(fname, 'wb')
                frontmatter.dump(post, newfile)
                newfile.close()
