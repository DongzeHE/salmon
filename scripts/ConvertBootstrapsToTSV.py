import gzip
import struct
import argparse
import os
import logging
import logging.handlers
import sys
import errno   

# from: http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def main(args):
    logging.basicConfig(level=logging.INFO)
    quantDir = args.quantDir
    bootstrapFile = os.path.sep.join([quantDir, "aux", "bootstrap", "bootstraps.gz"])
    nameFile = os.path.sep.join([quantDir, "aux", "bootstrap", "names.tsv.gz"])
    if not os.path.isfile(bootstrapFile):
       logging.error("The required bootstrap file {} doesn't appear to exist".format(bootstrapFile)) 
       sys.exit(1)
    if not os.path.isfile(nameFile):
       logging.error("The required transcript name file {} doesn't appear to exist".format(nameFile)) 
       sys.exit(1)
    
    txpNames = None
    with gzip.open(nameFile) as nf:
        txpNames = nf.read().strip().split('\t')
    
    ntxp = len(txpNames)
    logging.info("Expecting bootstrap info for {} transcripts".format(ntxp))
    
    s = struct.Struct('@' + 'd' * ntxp)
    numBoot = 0
    outDir = args.outDir
    if os.path.exists(outDir):
        if os.path.isfile(outDir):
            logging.error("The requested output directory {} already exists, but is a file".format(outDir))
            sys.exit(1)
        else:
            logging.warn("The requested output directory {} already exists --- any existing bootstraps may be overwritten".format(outDir))
    else:
        mkdir_p(outDir)
    
    outFile = os.path.sep.join([outDir, 'quant_bootstraps.tsv'])
    with open(outFile,'w') as ofile:
        # write the header
        ofile.write('\t'.join(txpNames) + '\n')
        
        # Now, iterate over the bootstrap samples and write each
        with gzip.open(bootstrapFile) as bf:
            while True:
                try:
                    x = s.unpack_from(bf.read(s.size))
                    xs = map(str, x)
                    ofile.write('\t'.join(xs) + '\n')
                    numBoot += 1
                except:
                    logging.info("read all bootstrap values")
                    break

    logging.info("wrote {} bootstrap samples".format(numBoot))
    logging.info("converted bootstraps successfully.")

if __name__ == "__main__":
   parser = argparse.ArgumentParser(description="Convert bootstrap results to text format") 
   parser.add_argument('quantDir', type=str, help="path to (sailfish / salmon) quantification directory")
   parser.add_argument('outDir', type=str, help="path to directory where results should be written")
   args = parser.parse_args()
   main(args)
