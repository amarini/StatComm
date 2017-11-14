### Original Author: Andrea Carlo Marini
### Date: 9/11/2017

import ROOT 
from array import array

# construct model and datacard
# type = cut & count / pdf
# bkg = yes / no

class Model():
    def __init__(self):
        self.type="c&c" ## pdf
        self.w = None
        ## truth bins
        self.nbins_x = 10
        ## reco bins
        self.nbins_y = 10
        ## ntruth events
        self.nevents=1000
        self.bkg=False ## non resonant bkg
        self.nbkg=100
        ## smearings, and efficiencies
        self.smearings = [0.75,.10,.025] ## diagonal, off-diagonola, 2nd ...
        self.eff = [.85,.85,.90,.90,.92,.92,.93,.94,.95,.99]  ## one per bin

        ###output file name
        self.fname = "workspace.root"
        self.dname = "datacard.txt"

    def run(self):
        self.doModel()
        self.doWorkspace()
        self.doDatacard()
        return self

    def doModel(self):
        xmin=0.
        xmax=10.
        self.x_cont = ROOT.RooRealVar("x_cont","x",xmin,xmax)
        self.pdf_cont = ROOT.RooGenericPdf("pt-sig","@0*@0*@0*TMath::Exp(-@0)",ROOT.RooArgList(self.x_cont))
        # this actually lives on the reco specturm
        self.bkg_cont = ROOT.RooGenericPdf("pt-bkg","Exp(-@0)",ROOT.RooArgList(self.x_cont))
        #self.cdf_pt = self.pt_cont.createCdf()

        ### 
        ## binned model
        self.x_th1 = ROOT.TH1D("x_th1","binned version of truth model",self.nbins_x, xmin,xmax)
        for i in range(0,self.nbins_x):
            rangename = "truth_range_%d"%i
            low  = i 
            high = i+1
            self.x_cont . setRange(rangename, low,high)
            count = self.pdf_cont.createIntegral(ROOT.RooArgSet(self.x_cont),ROOT.RooArgSet(self.x_cont),rangename).getVal() * self.nevents
            self.x_th1 .SetBinContent( self.x_th1.FindBin(i+0.5), count)
        ## construct smearing matrix
        ## y = M.x + b
        self.Mhat=ROOT.TH1D("Mhat","response probability matrix (X=truth, Y=Reco)",self.nbins_x,xmin,xmax,self.nbins_y,xmin,xmax)
        for i in range(0,self.nbins_x):
            for j in range(0,self.nbins_y):
                binX= self.Mhat.GetXaxis().FindBin(i+0.5)
                binY= self.Mhat.GetYaxis().FindBin(j+0.5)
                if len(self.smearings) >abs(i-j): self.Mhat.SetBinContent(binX,binY, self.smearings[abs(i-j)])
        # normalize Mhat to 1 per gen lines times efficiencies (are in truth dimension efficiencies)
        for i in range(0,self.nbins_x):
            binX= self.Mhat.GetXaxis().FindBin(i+0.5)
            S=0.
            for j in range(0,self.nbins_y):
                binY= self.Mhat.GetYaxis().FindBin(j+0.5)
                S+= self.Mhat.GetBinContent(binX,binY)
            for j in range(0,self.nbins_y):
                binY= self.Mhat.GetYaxis().FindBin(j+0.5)
                c= self.Mhat.GetBinContent(binX,binY)
                self.Mhat.SetBinContent(binX,binY, c * self.eff[i]/S )
        ## construct background
        self.b_th1 = ROOT.TH1("b_th1","background count in each bin",self.nbins_y,xmin,xmax)
        if self.bkg:
            for i in range(0,self.nbins_y):
                rangename = "bkg_range_%d"%i
                low  = i 
                high = i+1
                self.x_cont . setRange(rangename, low,high)
                count = self.pdf_cont.createIntegral(ROOT.RooArgSet(self.x_cont),ROOT.RooArgSet(self.x_cont),rangename).getVal() * self.nbkg
                self.b_th1 .SetBinContent( self.b_th1.FindBin(i+0.5), count)
            
        ## construct reco y = Mhat . x + b
        self.y_th1 = ROOT.TH1D("y_th1","binned version of reco model",self.nbins_y, xmin,xmax)
        for j in range(0,self.nbins_y):
            binY= self.Mhat.GetYaxis().FindBin(j+0.5)
            S=0.
            for i in range(0,self.nbins_x):
                binX= self.Mhat.GetXaxis().FindBin(i+0.5)
                m = self.Mhat.GetBinContent(binX,binY)
                x = self.x_th1.GetBinContent(binX)
                S+= m*x
            b = self.b_th1.GetBinContent(binY)
            y= S+b
            self.y_th1.SetBinContent(binY,y)

        ## construct M for future references / RooUnfold way
        self.M=ROOT.TH1D("M","response matrix (X=truth, Y=Reco)",self.nbins_x,xmin,xmax,self.nbins_y,xmin,xmax)
        for i in range(0,self.nbins_x):
            for j in range(0,self.nbins_y):
                binX= self.Mhat.GetXaxis().FindBin(i+0.5)
                binY= self.Mhat.GetYaxis().FindBin(j+0.5)
                c = self.Mhat.GetBinContent(binX,binY)
                x = self.x_th1.GetBinContent(binX)
                self.M.SetBinContent(binX,binY,c * x) 

    def Import(self,obj):
        getattr(self.w,'import')(obj,ROOT.RooCmdArg())

    def doWorspace(self):
        self.w = ROOT.RooWorkspace("w","w")
        ##self.pdf = ROOT.TF1("myfunc","x*x*x*TMath::Exp(-x)/5.9380",0,10)
        #create observable x (truth)
        print "-> construct real or fake pdfs for each entry in the matrix" 
        self.mgg = ROOT.RooRealVar("mgg","mgg",110,150)
        self.MH = ROOT.RooRealVar("MH","MH",125.)

        self.Import(self.mgg)
        self.Import(self.MH )
        
        if opts.type =='pdf':
            self.sigmaD = ROOT.RooRealVar("sigmaD","sigma diagonal elements",1.)
            self.sigmaO = ROOT.RooRealVar("sigmaO","sigma off-diagonal elements",2.)

            self.Import(self.sigmaD)
            self.Import(self.sigmaO)

        for i in range(0,self.nbins_x):
            for j in range(0,self.nbins_y):
                name = "GenBin%d_RecoBin%d"%(i,j)

                binX= self.Mhat.GetXaxis().FindBin(i+0.5)
                binY= self.Mhat.GetYaxis().FindBin(j+0.5)

                norm = ROOT.RooRealVar(name +"_norm","normalization of xxx",self.M.GetBinContent(binX,binY)
                if self.type == 'c&c':
                    pdf = ROOT.RooUniform(name,"Fake pdf for "+name,self.mgg)
                elif self.type == 'pdf':
                    if i==j:pdf = ROOT.Gaussian(name,"Gauss pdf for "+name,self.mgg,self.MH,self.sigmaD)
                    else:pdf = ROOT.Gaussian(name,"Gauss pdf for "+name,self.mgg,self.MH,self.sigmaO)
                self.Import(norm)
                self.Import(pdf)

        if self.bkg:
            if opts.type =='pdf':
                self.tau = ROOT.RooRealVar("tau","tau for bkg",-0.2)
                self.Import(self.sigmaD)

            for j in range(0,self.nbins_y):
                name = "Bkg_RecoBin%d"%(j)
                binY= self.Mhat.GetYaxis().FindBin(j+0.5)
                norm = ROOT.RooRealVar(name +"_norm","normalization of xxx",self.b_th1.GetBinContent(binY))
                
                if self.type=='c&c':
                    pdf = ROOT.RooUniform(name,"Fake pdf for "+name,self.mgg)
                elif self.type == 'pdf':
                    pdf = ROOT.RooExponential(name,"Exp pdf for "+name,self.mgg,self.tau)

                self.Import(norm)
                self.Import(pdf)
                    

        print "-> writing worspace to file",self.fname
        self.w.writeToFile(self.fname)
        print "-> adding  histograms to",self.fname
        self.fOut = ROOT.TFile.Open(self.fname,"UPDATE")
        self.fOut.cd()
        self.y_th1.Write()
        self.x_th1.Write()
        self.Mhat.Write()
        self.M.Write()
        self.fOut.Close()

    def doDatacard(self):
        self.datacard=open(self.dname,"w")
        self.datacard.write("------------------------\n")
        self.datacard.write("## Automatic created by makeModel\n")
        self.datacard.write("## Original Author: Andrea Carlo Marini\n")
        self.datacard.write("## Original Date: 9 Nov 2017\n")
        self.datacard.write("------------------------\n")
        self.datacard.write("* ibin\n")
        self.datacard.write("* jbin\n")
        self.datacard.write("* kbin\n")
        self.datacard.write("------------------------\n")
        ## shapes declaration
        #for i in range(0,self.nbins_x):
        #    for j in range(0,self.nbins_y):
        #name = "GenBin%d_RecoBin%d"%(i,j)
        #name = "Bkg_RecoBin%d"%(j)
        self.datacard.write("shape * * "+self.fname+" w:$PROCESS_$CHANNEL\n")
        self.datacard.write("------------------------\n")
        self.datacard.write("bin" + '\t'.join( ['RecoBin%d'%j for j in range(0,self.nbins_y) ] ) + '\n')
        self.datacard.write("observation" + '\t'.join( ['-1'%j for j in range(0,self.nbins_y) ] ) + '\n')
        ## observation
        self.datacard.write("------------------------\n")
        binline = "bin"
        procline = "process"
        procline2 = "process"
        rateline = "rate"

        for i in range(0,self.nbins_x):
            for j in range(0,self.nbins_y):
                binline +="\t"+'RecoBin%d'%j 
                procline += "\t"+'GenBin%d'%i
                procline2 += "\t"+'-%d'%i
                rateline += "\t" +"1"

        if self.bkg:
            for j in range(0,self.nbins_y):
                binline +="\t"+'RecoBin%d'%j 
                procline += "\t"+'Bkg'
                procline2 += "\t"+'1' ## >0: bkg ; <=0: sig
                rateline += "\t" +"1"

        self.datacard.write(binline +"\n"+ procline + "\n" + procline2+"\n" + rateline +"\n")
        ## expected
        self.datacard.write("------------------------\n")
        ## systematics

        ## write regularization lines

        ## write commands
        rootname = re.sub('.txt','.root',self.dname)
        self.datacard.write("\n")
        self.datacard.write("###############################\n")
        self.datacard.write("## Requsites for regularization studies:\n")
        self.datacard.write("##  git pull git@github.com:amarini/HiggsAnalysis-CombinedLimit/topic_regularization2016\n")
        self.datacard.write("##                             \n")
        self.datacard.write("## Commands:\n")
        self.datacard.write("## text2workspace.py -X-allow-no-background -o "+rootname+" "+self.dname+"\n")
        self.datacard.write("##   -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO map='.*Bin%d.*:r_Bin%d[1,-1,20]'\n")
        self.datacard.write("## combine -M MultiDimFit "+rootname+"\n")
        self.datacard.write("## combine -M MultiDimFit --algo=grid --points=100 -P GenBin1 --floatOtherPOIs=1 "+rootname+"\n")
        self.datacard.write("###############################\n")
        self.datacard.close()

########################
##        MAIN        ##
########################
if __name__=="__main__":
    model=Model()
    model.type='pdf'
    model.run()
    print "---- DONE ----"
