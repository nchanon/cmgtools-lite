import os
import ROOT
from ROOT import TFile, TH2F

from PhysicsTools.Heppy.analyzers.core.Analyzer import Analyzer


# for eta the abs is for the parameter at function call
def eta_binned(eta_param):
    if(0 <= eta_param and eta_param < 0.9):
        return 1
    elif(0.9 <= eta_param and eta_param < 1.2):
        return 2   
    elif(1.2 <= eta_param and eta_param < 2.1):
        return 3
    elif(2.1 <= eta_param and eta_param < 2.4):
        return 4
 
def pt_binned(pt_param):
    if(20 <= pt_param and pt_param < 25):
        return 1
    elif(25 <= pt_param and pt_param < 30):
        return 2         
    elif(30 <= pt_param and pt_param < 40):
        return 3
    elif(40 <= pt_param and pt_param < 50):
        return 4 
    elif(50 <= pt_param and pt_param < 60):
        return 5 
    elif(60 <= pt_param and pt_param <= 120):
        return 6   

def pt_binned_IsoMu27(pt_param):
    if(29 <= pt_param and pt_param < 32):
        return 1       
    elif(32 <= pt_param and pt_param < 40):
        return 2
    elif(40 <= pt_param and pt_param < 50):
        return 3 
    elif(50 <= pt_param and pt_param < 60):
        return 4 
    elif(60 <= pt_param and pt_param < 120):
        return 5 
    elif(120 <= pt_param and pt_param < 200):
        return 6
    elif(200 <= pt_param and pt_param <= 1200):
        return 7 
        
def pt_binned_Mu50(pt_param):
    if(52 <= pt_param and pt_param < 55):
        return 1
    elif(55 <= pt_param and pt_param < 60):
        return 2         
    elif(60 <= pt_param and pt_param < 120):
        return 3
    elif(120 <= pt_param and pt_param < 200):
        return 4 
    elif(200 <= pt_param and pt_param <= 1200):
        return 5


class MuonSFARC(Analyzer):

    def __init__(self, cfg_ana, cfg_comp, looperName):
        super(MuonSFARC, self).__init__(cfg_ana, cfg_comp, looperName)
        
        rootfname_id = '/'.join([os.environ["CMSSW_BASE"],
                              'src/CMGTools/TTbarTime/data/RunBCDEF_SF_ID.root'])                       
        rootfname_iso = '/'.join([os.environ["CMSSW_BASE"],
                              'src/CMGTools/TTbarTime/data/RunBCDEF_SF_ISO.root'])
        rootfname_trigger = '/'.join([os.environ["CMSSW_BASE"],
                              'src/CMGTools/TTbarTime/data/EfficienciesAndSF_RunBtoF_Nov17Nov2017.root'])
                              
        self.mc_sfm_id_file = TFile(rootfname_id)
        self.mc_sfm_id_hist = self.mc_sfm_id_file.Get('NUM_TightID_DEN_genTracks_pt_abseta')                              
                
        self.mc_sfm_iso_file = TFile(rootfname_iso)
        self.mc_sfm_iso_hist = self.mc_sfm_iso_file.Get('NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta')                              
        
        self.mc_sfm_trig_isomu27_file = TFile(rootfname_trigger)
        self.mc_sfm_trig_isomu27_hist = self.mc_sfm_trig_isomu27_file.Get('IsoMu27_PtEtaBins/pt_abseta_ratio')
        self.mc_sfm_trig_mu50_hist    = self.mc_sfm_trig_isomu27_file.Get('Mu50_PtEtaBins/pt_abseta_ratio')
        
    def process(self, event):

        sfm_id_weight = 1.    
        sfm_iso_weight = 1.
        sfm_trig_isomu27_weight = 1.
        sfm_trig_mu50_weight = 1.
        muons = getattr(event, self.cfg_ana.muons)    
        for muon in muons: # caution abs(eta)
            if(muon.pt() <= 1200):
                if(muon.pt() >= 29):
                    sfm_trig_isomu27_weight *= self.mc_sfm_trig_isomu27_hist.GetBinContent(pt_binned_IsoMu27(muon.pt()), eta_binned(abs(muon.eta())))
                if(muon.pt() >= 52):
                    sfm_trig_mu50_weight    *= self.mc_sfm_trig_mu50_hist.GetBinContent(pt_binned_Mu50(muon.pt()), eta_binned(abs(muon.eta())))
                if(muon.pt() <= 120):
                    sfm_id_weight  *= self.mc_sfm_id_hist.GetBinContent(pt_binned(muon.pt()), eta_binned(abs(muon.eta())))
                    sfm_iso_weight *= self.mc_sfm_iso_hist.GetBinContent(pt_binned(muon.pt()), eta_binned(abs(muon.eta())))
            
        setattr(event, 'sfmIdWeight', sfm_id_weight)
        setattr(event, 'sfmIsoWeight', sfm_iso_weight)
        setattr(event, 'sfmTrigIsoMu27Weight', sfm_trig_isomu27_weight)
        setattr(event, 'sfmTrigMu50Weight', sfm_trig_mu50_weight)
        event.eventWeight *= event.sfmIdWeight
        event.eventWeight *= event.sfmIsoWeight
        event.eventWeight *= event.sfmTrigIsoMu27Weight
        event.eventWeight *= event.sfmTrigMu50Weight
        
        
        