'''
Count coded lines of all projects
'''
from fancytools.utils.countLines import countLines
from fancytools.os.PathStr import PathStr

d = PathStr.getcwd().dirname()

countLines([
            d.join('dataArtist'),
            d.join('fancyTools'),
            d.join('fancyWidgets'),
            d.join('appBase'),
            d.join('imgprocessor'),
            #d.join('pvimgprocessor'),
            d.join('interactiveTutorial'),
            d.join('headerSetter') 
           ],exclude_folders_containing=("DUMP",'dist', 'dev', 'build','fancytools3'),
             exclude_blank_lines=True,
             exclude_commented_lines=True,
             count_only_py_files=True)