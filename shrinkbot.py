import imp,os,base64,zlib,argparse

# shrinkbot.py by ramk13
# https://github.com/ramk13/robotgame/

def main():

    try:
        imp.find_module('minipy')
        import minipy
    except ImportError:
        print 'Missing minipy'
        print 'get it here: http://github.com/gareth-rees/minipy'
        print 'install with \'setup.py -install\' in the minipy folder'
        return

    parser = argparse.ArgumentParser(prog='shrinkbot',\
        description='Shrink a robotgame robot using minipy/zlib/base64.')

    parser.add_argument('robot', metavar='robot_file', help='Robot to shrink')
    parser.add_argument('--output', '-o', \
                 help="output file (default: appends _shrunken to the original file name)")
    parser.add_argument('--delete_minipy', '-d', action='store_true',\
                 help="delete the minipy intermediate file")
        
    args = parser.parse_args()
    infile = args.robot
    if os.path.isfile(infile):
        base = os.path.basename(infile)
        robotname = os.path.splitext(base)[0]
        outfile_minipy = robotname + '_minipy.py'
        if args.output is not None:
            outfile_shrink = args.output
        else:
            outfile_shrink = robotname + '_shrunken.py'
    else:
        parser.error("invalid/missing file")

    fid=open(infile)
    robot_original=fid.read()
    fid.close()
    len_original = len(robot_original)
    print 'original: %5i' % len_original
    
    # code taken from here:
    # http://stackoverflow.com/questions/7032031/python-regex-to-remove-comments
    import tokenize
    import io

    def nocomment(s):
        result = []
        g = tokenize.generate_tokens(io.BytesIO(s).readline)  
        for toknum, tokval, _, _, _  in g:
            # print(toknum,tokval)
            if toknum != tokenize.COMMENT:
                result.append((toknum, tokval))
        return tokenize.untokenize(result)

    robot_nocomments = nocomment(robot_original)
    len_nocomm = float(len(robot_nocomments))
    print 'w/o comm: %5i' % len_nocomm
        
    minipy.minify(infile, output=outfile_minipy, rename=True, preserve='Robot,act', docstrings=True)
    fid=open(outfile_minipy)
    robot_minify=fid.read()
    fid.close()
    if args.delete_minipy:
        os.remove(outfile_minipy)
    len_minify = len(robot_minify)
    print 'minipy  : %5i  (%2i%% of original w/o comm)' % (len_minify,len_minify/len_nocomm*100)

    robot_zlib = zlib.compress(robot_minify,9)
    print 'zlib    : %5i' % len(robot_zlib)
    
    robot_encoded = base64.b64encode(robot_zlib)
    len_encoded = len(robot_encoded)
    print 'base64  : %5i' % len_encoded
    
    fid=open(outfile_shrink ,'w')
    final_string = 'import base64,zlib\nexec zlib.decompress(base64.decodestring(\'' + robot_encoded + '\'))'
    len_final = len(final_string)
    fid.write(final_string)
    fid.close()

    print 'final   : %5i  (%2i%% of original w/o comm)' % (len_final,(len_final)/len_nocomm*100)
    
if __name__ == '__main__':
    main()
