#!/usr/bin/env python
import shutil, os, argparse, sys, stat
import requests
import csv, io
from __builtin__ import type



class SRAUtils:
    @staticmethod
    def getInfoTableFromSearchTerm(search):
        payload = {"save": "efetch","db": "sra","rettype" : "runinfo", "term" : search };
        r = requests.get('http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi', params=payload)
        if 200 ==  r.status_code:
            if r.text.isspace():
                raise Exception("Got blank string from " + str(r.url ))
            else:
                reader_list = csv.DictReader(io.StringIO(r.text))
                infoRows = []
                for row in reader_list:
                    infoRows.append(row)
                if 0 == len(infoRows):
                    raise Exception('Found %d entries in SRA for "%s" when expecting at least 1' % (len(infoRows), search))
                else:        
                    return infoRows
                return infoRows
        else:
            raise Exception("Error in downloading from " + str(r.url) + " got response code " + str(r.status_code))
        
    @staticmethod
    def getSraUrlFromRunAccession(accesion):
        if not type(accesion) is str:
            raise Exception("Error in getSraUrlFromRunAccession: accesion should be str, not " + str(type(accesion)))
        if len(accesion) < 7:
            raise Exception("Error in getSraUrlFromRunAccession: accession should be least 7 character long, not " + str(len(accesion)) + ", for " + str(accesion))
        
        if not accesion.startswith("ERR") and not accesion.startswith("SRR"):
            raise Exception("Error in getSraUrlFromRunAccession: accession should start with either ERR or SRR, not " + str(accesion[0:3]) )
        
        template = "ftp://ftp-trace.ncbi.nlm.nih.gov/sra/sra-instant/reads/ByRun/sra/{PREFIX}/{PREFIX}{PREFIXNUMS}/{ACCESION}/{ACCESION}.sra"
        return template.format(PREFIX = accesion[0:3], PREFIXNUMS = accesion[3:6], ACCESION = accesion)
    
    @staticmethod
    def getInfoFromRunAcc(run):
        if not run.startswith("ERR") and not run.startswith("SRR"):
            raise Exception("run should start with ERR or SRR, not: " + run)
        infoTab = SRAUtils.getInfoTableFromSearchTerm(run)
        runInfo = []
        for row in infoTab:
            if run == str(row.get('Run')):
                runInfo.append(row)
        if 0 == len(runInfo):
            raise Exception('Found %d entries in SRA for "%s" when expecting at least 1' % (len(runInfo), run))
        else:
            return runInfo

    @staticmethod
    def getInfoFromSubmissionAcc(submission):
        if not submission.startswith("ERA") and not submission.startswith("SRA"):
            raise Exception("submission should start with ERR or SRR, not: " + submission)
        infoTab = SRAUtils.getInfoTableFromSearchTerm(submission)
        runInfo = []
        for row in infoTab:
            if submission == str(row.get('Submission')):
                runInfo.append(row)
        if 0 == len(runInfo):
            raise Exception('Found %d entries in SRA for "%s" when expecting at least 1' % (len(runInfo), submission))
        else:
            return runInfo    
        
    @staticmethod
    def getInfoFromSampleAcc(sample):
        if not sample.startswith("ERS") and not sample.startswith("SRS"):
            raise Exception("sample should start with ERS or SRS, not: " + sample)
        infoTab = SRAUtils.getInfoTableFromSearchTerm(sample)
        runInfo = []
        for row in infoTab:
            if sample == str(row.get('Sample')):
                runInfo.append(row)
        if 0 == len(runInfo):
            raise Exception('Found %d entries in SRA for "%s" when expecting at least 1' % (len(runInfo), sample))
        else:
            return runInfo
        
    @staticmethod
    def getInfoFromProjectAcc(project):
        if not project.startswith("ERP") and not project.startswith("SRP"):
            raise Exception("project should start with ERP or SRP, not: " + project)
        infoTab = SRAUtils.getInfoTableFromSearchTerm(project)
        runInfo = []
        for row in infoTab:
            if project == str(row.get('SRAStudy')):
                runInfo.append(row)
        if 0 == len(runInfo):
            raise Exception('Found %d entries in SRA for "%s" when expecting at least 1' % (len(runInfo), project))
        else:
            return runInfo
        
    @staticmethod
    def getInfoFromExperimentAcc(experiment):
        if not experiment.startswith("ERX") and not experiment.startswith("SRX"):
            raise Exception("experiment should start with ERX or SRX, not: " + experiment)
        infoTab = SRAUtils.getInfoTableFromSearchTerm(experiment)
        runInfo = []
        for row in infoTab:
            if experiment == str(row.get('Experiment')):
                runInfo.append(row)
        if 0 == len(runInfo):
            raise Exception('Found %d entries in SRA for "%s" when expecting at least 1' % (len(runInfo), experiment))
        else:        
            return runInfo
    
    @staticmethod
    def getInfoFromBioProjectAcc(bioProject):
        if not bioProject.startswith("PRJNA"):
            raise Exception("bioProject should start with PRJNA, not: " + bioProject)
        infoTab = SRAUtils.getInfoTableFromSearchTerm(bioProject)
        runInfo = []
        for row in infoTab:
            if bioProject == str(row.get('BioProject')):
                runInfo.append(row)
        if 0 == len(runInfo):
            raise Exception('Found %d entries in SRA for "%s" when expecting at least 1' % (len(runInfo), bioProject))
        else:        
            return runInfo   
    
    
        
    @staticmethod
    def getInfoFromSRAIdentifier(identifier):
        if identifier.startswith("ERX") or identifier.startswith("SRX"):
            return SRAUtils.getInfoFromExperimentAcc(identifier)
        elif identifier.startswith("ERP") or identifier.startswith("SRP"):
            return SRAUtils.getInfoFromProjectAcc(identifier)
        elif identifier.startswith("ERS") or identifier.startswith("SRS"):
            return SRAUtils.getInfoFromSampleAcc(identifier)
        elif identifier.startswith("ERR") or identifier.startswith("SRR"):
            return SRAUtils.getInfoFromRunAcc(identifier)
        elif identifier.startswith("ERA") or identifier.startswith("SRA"):
            return SRAUtils.getInfoFromSubmissionAcc(identifier)
        elif identifier.startswith("PRJNA"):
            return SRAUtils.getInfoFromBioProjectAcc(identifier)
        else:
            raise Exception("Error, unrecognized prefix for sra Identifier " + str(identifier))


def parse_args_sraIdentifier():
    parser = argparse.ArgumentParser()
    parser.add_argument('--identifiers', type=str, help = "A list of comma separated SRA identifiers e.g. SRP046206,SRX188939,SRS807544,SRR1759594,PRJNA63661",  required = True)
    parser.add_argument('--outStub', type=str, help = "An output stub for info and sra urls output files",  required = True)
    parser.add_argument('--overWrite', action = "store_true", help = "Overwrite files if they already exist")
    return parser.parse_args()

def runGetRunsFromSampleAcc():
    args = parse_args_sraIdentifier()
    identifiers = args.identifiers.split(",")
    #sys.stdout.write(str("identifier") + "\t" + str("run") + "\t" + "url" + "\n")
    outUrlsFnp = args.outStub + "_urls.tab.txt"
    outInfoFnp = args.outStub + "_info.tab.txt"
    if os.path.exists(outUrlsFnp) and not args.overWrite:
        raise Exception("File " + outUrlsFnp + " already exists, use --overWrite to over write it")
    if os.path.exists(outInfoFnp) and not args.overWrite:
        raise Exception("File " + outInfoFnp + " already exists, use --overWrite to over write it")
    with open(outUrlsFnp, "w") as outUrlsFile:
        with open(outInfoFnp, "w") as outInfoFile:
            outUrlsFile.write(str("identifier") + "\t" + str("run") + "\t" + "url" + "\n")
            identifierCount = 0
            for identifier in identifiers:
                tab = SRAUtils.getInfoFromSRAIdentifier(identifier)
                if 0 == identifierCount:
                    outInfoFile.write("\t".join(tab[0].keys()) + "\n")
                for row in tab:
                    outUrlsFile.write(str(identifier) + "\t" + row.get("Run") + "\t" + SRAUtils.getSraUrlFromRunAccession(str(row.get("Run"))) + "\n")
                    outInfoFile.write("\t".join(row.values()) + "\n")
                identifierCount = identifierCount + 1

if __name__ == "__main__":
    runGetRunsFromSampleAcc()
    
    
    