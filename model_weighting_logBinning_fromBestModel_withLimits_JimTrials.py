##NOTE: in order to display the histogram, the script must be run with the -i option
import numpy as np
import matplotlib
#matplotlib.use("macOSX")
#matplotlib.use("TKAgg")
import matplotlib.pyplot as plt
import os
import ROOT
#import sys
from ROOT import TH1F, TH1D, TH2
from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TFile, TLine, TGraph, TAttFill, TColor, TLegend
from ROOT import TCanvas

from ROOT import gROOT, gPad, gStyle
from scipy.interpolate import CubicSpline
from scipy.interpolate import spline
#from scipy.interpolate import InterpolatedUnivariateSpline as spline
from matplotlib.lines import Line2D
from array import array

# The PyEBL python class contains methods useful for handling EBL SEDs.
import PyEBL
# The PyBlazar python class contains methods useful for handling blazar spectra
# and their associated optical depth calculations, etc.
import PyBlazar
from ebltable.ebl_from_model import EBL
#plt.ion()

'''
hist_1 = TH1F('hist_1', 'Intensity @ #lambda = 1#mum', 50, 1, 32)
hist_2 = TH1F('hist_1', 'Intensity @ #lambda = 84#mum', 50, 1, 32)
hist_3 = TH1F('hist_1', 'Intensity @ #lambda = 500#mum', 50, 1, 32)
hist_4 = TH1F('hist_1', 'Intensity @ #lambda = 833#mum', 50, 1, 32)
'''

#DEFINE PATHS!!!
path_to_intensity_file = '/Users/mateo/Documents/HAWC/EBL/EBLmodel_likelihood/Model_Weigth/Model_Intensity_Weights/'
path_to_weights_file = '/Users/mateo/Documents/HAWC/EBL/EBLmodel_likelihood/linearIntensities/mrk421_gp_SSC_ECPL_EBL_loglike_Fixed_FullRange_12Knots_1nuI_50nuI_100um_linIntensities/'

# FIRST!! Retrieve Model lambda-Intensities
#namewithdir_int = os.path.join(path_to_intensity_file,'EBLintensities_knotfree_logScale_1e4sample_fromUpperLowerBounds_includingStandardModels.dat')
namewithdir_int = os.path.join(path_to_intensity_file,'EBLintensities_lambda12_1_100um_logScale_FULLRANGE_1nuI_50nuI_1to10k.dat')

f_modelIntensities=open(namewithdir_int, 'r')


d_modelIntensities = f_modelIntensities.readlines()

#reader = csv.reader(f, delimiter=' ', skipinitialspace=True)
#first_row = next(reader)
#num_cols = len(first_row)

#lamb=[1,  1.77828,  3.68228,  5.62341,  90,  17.7828,  31.6228,  56.2341, 900,  177.828,  368.228,  562.341]
nmodels=10000
nlambda=12
#lamb=[5,  6.95764,  7.339,  8.8914,  90.7722,  13.9508,  15.8114,  19.1559,  23.2079,  28.1171,  34.0646,  41.2702]
#lamb=[1,  84.25,  687.5,  250.75,  334,  417.25,  500.5,  583.75,  667,  750.25,  833.5,  968.75]
lamb= np.logspace(np.log10(1),np.log10(100),nlambda, endpoint=True)

Intensity=np.empty([nmodels,len(lamb)])
Intensity_best=np.empty([len(lamb)])
## Create array with intensities for each model (first index) and wavelenght (second index)

#retrieve best model line
namewithdir_best = os.path.join(path_to_weights_file,'BestModel_like.txt')
f_best_model=open(namewithdir_best, 'r')
best_model_number_line = f_best_model.readlines()
for x in best_model_number_line:
	best_model_number= int(x.split(' ')[11])

print "The 'chosen' model is: ", best_model_number
i=-1
for x in d_modelIntensities:
	#Intensity.append([])
        i=i+1;
	for s in range(len(lamb)):
		I=float(x.split('  ')[s])
		Intensity[i][s]=I
		if(i==best_model_number-1):
			Intensity_best[s]=I

#print Intensity_best


##Define histograms with log geometric spaced binning
hist_array_preWeight=[]
hist_array=[]
#hist = TH1F('hist', 'Intensity', 90, -1, 32)
binning = 60
graph_array=[]
intensitybins=[]

for i in range(binning+1):
	intensitybins.append(10**((np.log10(50)/binning)*i))

for l in range(len(lamb)):
	hist_name_pre="hIntensity@ #lambda={0}#mum pre-Weight".format(str(round(lamb[l],2)))
	hist_name="hIntensity@ #lambda={0}#mum".format(str(round(lamb[l],2)))
	#print hist_name
	#hist = TH1F(hist_name, hist_name, 40, -1, 15)
	#hist = TH1F(hist_name, hist_name, binning, min(Intensity[:,l]),max(Intensity[:,l]))
	hist_pre = TH1D(hist_name_pre, hist_name_pre, binning, array('d',intensitybins))
	hist = TH1D(hist_name, hist_name, binning, array('d',intensitybins))
	hist_array_preWeight.append(hist_pre)
	hist_array.append(hist)

### SECOND!! Create array with weights from lambda-conditioning
namewithdir_lambWeig = os.path.join(path_to_intensity_file,'intensityweights_lambda12_1_100um_logScale_FULLRANGE_1nuI_50nuI.root')
f = ROOT.TFile.Open(namewithdir_lambWeig)
hist=f.Get('weight23')
#print hist.GetBinContent(3)


### THIRD!! Create array with weights from likelihood

namewithdir_weight = os.path.join(path_to_weights_file,'Model_ProbValues_likelihood.txt')
f_results=open(namewithdir_weight, 'r')
#f_results=open('/home/mateo/Documents/HAWC/EBL/EBLmodel_likelihood/mrk501_gp_SSC_BPL_EBL_loglike_Fixed_FullRange/median/Model_ProbValues_likelihood.txt', 'r')
#f_results=open('/home/mateo/Documents/HAWC/EBL/EBLmodel_likelihood/mrk501_gp_SSC_BPL_EBL_loglike_Fixed_FromLimits/median/Model_ProbValues_likelihood.txt', 'r')
#f_results=open('/home/mateo/Documents/HAWC/EBL/EBLmodel_likelihood/._gp_SSC_ECPL_EBL_loglike_Fixed_FromLimits/median/Model_BIC_Categories_Ordered_ProbValues_Posterior.txt', 'r')
#f_results=open('/home/mateo/Documents/HAWC/EBL/EBLmodel_likelihood/._gp_SSC_ECPL_EBL_loglike_Fixed_AllRange_Subset_1e3/Model_BIC_Categories_Ordered_ProbValues_fromFits_gaus.txt', 'r')
model_probValues = f_results.readlines()

#Intensity_w=[]## weight for each model (1st index) and each lamba (2nd index)
Intensity_w=np.empty([nmodels,len(lamb)])


total_points = Intensity.size
Int_array = np.empty([total_points])
Int_array_spline = np.empty([nmodels])
lambda_array = np.empty([total_points])
#sigma_array = np.empty([total_points,total_points])
#cate_array = np.empty([total_points])
prob_array = np.empty([nmodels])
k=-1
i=-1
for x in model_probValues:
	model= x.split('  ')[0]
	prob= float(x.split('  ')[1])
	i=i+1
	prob_array[i]=prob

	for j in range(len(lamb)):
		k=k+1
                Int_array[k]=Intensity[i][j]
                lambda_array[k]=lamb[j]
		Intensity_w[i][j]=prob
#plot intensity weights for each lamba:


#hist_5.GetXAxis().SetTitle("bla")
#for i in range(len(lamb)):


lower_bound_68=np.zeros(shape=(len(lamb),hist_array[j].GetSize()))
lower_containment_68=np.zeros(shape=(len(lamb),hist_array[j].GetSize()))


lower_bound_90=np.zeros(shape=(len(lamb),hist_array[j].GetSize()))
lower_containment_90=np.zeros(shape=(len(lamb),hist_array[j].GetSize()))

lower_bound_95=np.zeros(shape=(len(lamb),hist_array[j].GetSize()))
lower_containment_95=np.zeros(shape=(len(lamb),hist_array[j].GetSize()))


higher_bound_68=np.zeros(shape=(len(lamb),hist_array[j].GetSize()))
higher_containment_68=np.zeros(shape=(len(lamb),hist_array[j].GetSize()))

higher_bound_90=np.zeros(shape=(len(lamb),hist_array[j].GetSize()))
higher_containment_90=np.zeros(shape=(len(lamb),hist_array[j].GetSize()))

higher_bound_95=np.zeros(shape=(len(lamb),hist_array[j].GetSize()))
higher_containment_95=np.zeros(shape=(len(lamb),hist_array[j].GetSize()))


low_bound_68=[]
high_bound_68=[]

low_bound_90=[]
high_bound_90=[]

low_bound_95=[]
high_bound_95=[]

line_low_array=[]
line_high_array=[]

line_MaxBin_array=[]
threshold = 0


for j in range(len(lamb)):
	I=[]

	for i in range(len(model_probValues)):

		I.append(Intensity[i][j])
		hist_array_preWeight[j].Fill(Intensity[i][j],Intensity_w[i][j])
		#hist_array_preWeight[j].Fill(Intensity[i][j])


	## Apply weight from lambda condition
	hist_weight_name="weight{0}".format(j)
	hist_weight=f.Get(hist_weight_name)

	for s in range(binning):
		bin_weight = hist_weight.GetBinContent(s+1)
		hist_array[j].SetBinContent(s+1,hist_array_preWeight[j].GetBinContent(s+1)*bin_weight)
	#print hist_array[j].Integral()
	##Normalize histograms
	hist_array[j].Scale(1/hist_array[j].Integral())

	## Get bin corresponding to best model Intensity value
	best_bin = hist_array[j].FindBin(Intensity_best[j])
	#print best_bin
	#First, lower bounds

	for l in reversed(range(0,best_bin)):

		ratio =  hist_array[j].Integral(l,best_bin)/hist_array[j].Integral()

		if (ratio > 0.34):
			lower_bound_68[j][l] = hist_array[j].GetBinCenter(l+1)
			lower_containment_68[j][l] = hist_array[j].Integral(l+1,best_bin)/hist_array[j].Integral()

		if (ratio > 0.45):
			lower_bound_90[j][l] = hist_array[j].GetBinCenter(l+1)
			lower_containment_90[j][l] = hist_array[j].Integral(l+1,best_bin)/hist_array[j].Integral()

		if (ratio > 0.475):
			lower_bound_95[j][l] = hist_array[j].GetBinCenter(l+1)
			lower_containment_95[j][l] = hist_array[j].Integral(l+1,best_bin)/hist_array[j].Integral()

	lower_bound_68[j]=np.flip(lower_bound_68[j])
        lower_containment_68[j]=np.flip(lower_containment_68[j])

	lower_bound_90[j]=np.flip(lower_bound_90[j])
        lower_containment_90[j]=np.flip(lower_containment_90[j])


	lower_bound_95[j]=np.flip(lower_bound_95[j])
        lower_containment_95[j]=np.flip(lower_containment_95[j])

	#Extract first 2 non-zero values of each array and interpolate to get accurate 0.68, 0.90 and 0.95 bounds

	################### Lower 0.68 bound ###################################
	if (len(np.trim_zeros(lower_bound_68[j]))>1):
		lower_bound_68_high = np.trim_zeros(lower_bound_68[j])[0]
		lower_bound_68_low= np.trim_zeros(lower_bound_68[j])[1]

		lower_containment_68_high = np.trim_zeros(lower_containment_68[j])[0]
		lower_containment_68_low = np.trim_zeros(lower_containment_68[j])[1]


		low_bound_68.append(((lower_bound_68_high-lower_bound_68_low)*0.34/(lower_containment_68_low-lower_containment_68_high))-(lower_containment_68_high*((lower_bound_68_high-lower_bound_68_low)/(lower_containment_68_low-lower_containment_68_high))-lower_bound_68_low))

		#print lower_bound_68_high," ",lower_bound_68_low," ",((lower_bound_68_high-lower_bound_68_low)*0.34/(lower_containment_68_low-lower_containment_68_high))-(lower_containment_68_high*((lower_bound_68_high-lower_bound_68_low)/(lower_containment_68_low-lower_containment_68_high))-lower_bound_68_low)


	elif (len(np.trim_zeros(lower_bound_68[j]))>0):
		low_bound_68.append(np.trim_zeros(lower_bound_68[j])[0])


	else:
		low_bound_68.append(min(Intensity[:,j]))

	################### Lower 0.90 bound ###################################
	if (len(np.trim_zeros(lower_bound_90[j]))>1):
		lower_bound_90_high = np.trim_zeros(lower_bound_90[j])[0]
		lower_bound_90_low= np.trim_zeros(lower_bound_90[j])[1]

		lower_containment_90_high = np.trim_zeros(lower_containment_90[j])[0]
		lower_containment_90_low = np.trim_zeros(lower_containment_90[j])[1]

		low_bound_90.append(((lower_bound_90_high-lower_bound_90_low)*0.45/(lower_containment_90_low-lower_containment_90_high))-(lower_containment_90_high*((lower_bound_90_high-lower_bound_90_low)/(lower_containment_90_low-lower_containment_90_high))-lower_bound_90_low))
		#print lower_bound_90_high," ",lower_bound_90_low," ",((lower_bound_90_high-lower_bound_90_low)*0.34/(lower_containment_90_low-lower_containment_90_high))-(lower_containment_90_high*((lower_bound_90_high-lower_bound_90_low)/(lower_containment_90_low-lower_containment_90_high))-lower_bound_90_low)


	elif (len(np.trim_zeros(lower_bound_90[j]))>0):
		low_bound_90.append(np.trim_zeros(lower_bound_90[j])[0])


	else:
		low_bound_90.append(min(Intensity[:,j]))

	################### Lower 0.95 bound ###################################

	if (len(np.trim_zeros(lower_bound_95[j]))>1):
		lower_bound_95_high = np.trim_zeros(lower_bound_95[j])[0]
		lower_bound_95_low= np.trim_zeros(lower_bound_95[j])[1]

		lower_containment_95_high = np.trim_zeros(lower_containment_95[j])[0]
		lower_containment_95_low = np.trim_zeros(lower_containment_95[j])[1]

		low_bound_95.append(((lower_bound_95_high-lower_bound_95_low)*0.475/(lower_containment_95_low-lower_containment_95_high))-(lower_containment_95_high*((lower_bound_95_high-lower_bound_95_low)/(lower_containment_95_low-lower_containment_95_high))-lower_bound_95_low))

	elif (len(np.trim_zeros(lower_bound_95[j]))>0):
		low_bound_95.append(np.trim_zeros(lower_bound_95[j])[0])


	else:
		low_bound_95.append(min(Intensity[:,j]))


	##################     NOW HIGHER BOUND #########################
	for l in range(best_bin,hist_array[j].GetSize()):

		ratio =  hist_array[j].Integral(best_bin,l)/hist_array[j].Integral()

		if (ratio > 0.34):
			higher_bound_68[j][l] = hist_array[j].GetBinCenter(l-1)
			higher_containment_68[j][l] = hist_array[j].Integral(best_bin,l-1)/hist_array[j].Integral()
		if (ratio > 0.45):
			higher_bound_90[j][l] = hist_array[j].GetBinCenter(l-1)
			higher_containment_90[j][l] = hist_array[j].Integral(best_bin,l-1)/hist_array[j].Integral()

		if (ratio > 0.475):
			higher_bound_95[j][l] = hist_array[j].GetBinCenter(l-1)
			higher_containment_95[j][l] = hist_array[j].Integral(best_bin,l-1)/hist_array[j].Integral()


	#Extract first 2 non-zero values of each array and interpolate to get accurate 0.68, 0.90 and 0.95 bounds

	################### higher 0.68 bound ###################################

	if (len(np.trim_zeros(higher_bound_68[j]))>1):
		higher_bound_68_high = np.trim_zeros(higher_bound_68[j])[0]
		higher_bound_68_low= np.trim_zeros(higher_bound_68[j])[1]

		higher_containment_68_high = np.trim_zeros(higher_containment_68[j])[0]
		higher_containment_68_low = np.trim_zeros(higher_containment_68[j])[1]


		high_bound_68.append(((higher_bound_68_high-higher_bound_68_low)*0.34/(higher_containment_68_high-higher_containment_68_low))-(higher_containment_68_low*((higher_bound_68_high-higher_bound_68_low)/(higher_containment_68_high-higher_containment_68_low))-higher_bound_68_low))

	elif (len(np.trim_zeros(higher_bound_68[j]))>0):
		high_bound_68.append(np.trim_zeros(higher_bound_68[j])[0])


	else:
		high_bound_68.append(max(Intensity[:,j]))


	################### higher 0.90 bound ###################################

	if (len(np.trim_zeros(higher_bound_90[j]))>1):
		higher_bound_90_high = np.trim_zeros(higher_bound_90[j])[0]
		higher_bound_90_low= np.trim_zeros(higher_bound_90[j])[1]

		higher_containment_90_high = np.trim_zeros(higher_containment_90[j])[0]
		higher_containment_90_low = np.trim_zeros(higher_containment_90[j])[1]


		high_bound_90.append(((higher_bound_90_high-higher_bound_90_low)*0.45/(higher_containment_90_high-higher_containment_90_low))-(higher_containment_90_low*((higher_bound_90_high-higher_bound_90_low)/(higher_containment_90_high-higher_containment_90_low))-higher_bound_90_low))

	elif (len(np.trim_zeros(higher_bound_90[j]))>0):
		high_bound_90.append(np.trim_zeros(higher_bound_90[j])[0])


	else:
		high_bound_90.append(max(Intensity[:,j]))

	################### higher 0.95 bound ###################################

	if (len(np.trim_zeros(higher_bound_95[j]))>1):
		higher_bound_95_high = np.trim_zeros(higher_bound_95[j])[0]
		higher_bound_95_low= np.trim_zeros(higher_bound_95[j])[1]

		higher_containment_95_high = np.trim_zeros(higher_containment_95[j])[0]
		higher_containment_95_low = np.trim_zeros(higher_containment_95[j])[1]


		high_bound_95.append(((higher_bound_95_high-higher_bound_95_low)*0.475/(higher_containment_95_high-higher_containment_95_low))-(higher_containment_95_low*((higher_bound_95_high-higher_bound_95_low)/(higher_containment_95_high-higher_containment_95_low))-higher_bound_95_low))

	elif (len(np.trim_zeros(higher_bound_95[j]))>0):
		high_bound_95.append(np.trim_zeros(higher_bound_95[j])[0])


	else:
		high_bound_95.append(max(Intensity[:,j]))




	#Plotting Estetics and bound lines
	hist_array[j].SetFillColorAlpha( 38, 0.7 )
	line_low_array.append(TLine(low_bound_68[j],0,low_bound_68[j],hist_array[j].GetBinContent(hist_array[j].GetXaxis().FindBin(low_bound_68[j]))))
	line_high_array.append(TLine(high_bound_68[j],0,high_bound_68[j],hist_array[j].GetBinContent(hist_array[j].GetXaxis().FindBin(high_bound_68[j]))))
	line_MaxBin_array.append(TLine(hist_array[j].GetXaxis().GetBinCenter(best_bin),0,hist_array[j].GetXaxis().GetBinCenter(best_bin),hist_array[j].GetBinContent(best_bin)))

	#Define regions to plot with tgraphs
	n_bins_region = 2*(hist_array[j].FindBin(high_bound_68[j])-hist_array[j].FindBin(low_bound_68[j]))
	#print n_bins_region/2
	graph=TGraph(2*n_bins_region)
	graph_array.append(graph)
	for l in range(0,n_bins_region/2):
		graph_array[j].SetPoint(2*l,hist_array[j].GetBinLowEdge(hist_array[j].FindBin(low_bound_68[j])+l),1.*hist_array[j].GetBinContent(hist_array[j].FindBin(low_bound_68[j])+l))

		graph_array[j].SetPoint(2*l+1,hist_array[j].GetBinLowEdge(hist_array[j].FindBin(low_bound_68[j])+l+1),1.*hist_array[j].GetBinContent(hist_array[j].FindBin(low_bound_68[j])+l))

		graph_array[j].SetPoint(2*n_bins_region-2*l-1,hist_array[j].GetBinLowEdge(hist_array[j].FindBin(low_bound_68[j])+l),0.*hist_array[j].GetBinContent(hist_array[j].FindBin(low_bound_68[j])+l))

		graph_array[j].SetPoint(2*n_bins_region-2*l-2,hist_array[j].GetBinLowEdge(hist_array[j].FindBin(low_bound_68[j])+l+1),0.*hist_array[j].GetBinContent(hist_array[j].FindBin(low_bound_68[j])+l))


	## define histograms for each lambda according to the calculated limits




##**** SAVING RESULTS TO FILE*******************##

namewithdir_results = os.path.join(path_to_weights_file,'UpperLower_Limits.dat')
f_results=open(namewithdir_results, 'w+')

for i in range(len(lamb)):
	print lamb[i]," ",Intensity_best[i]," ",low_bound_68[i]," ",high_bound_68[i]," ",low_bound_95[i]," ",high_bound_95[i]
	print >> f_results, lamb[i]," ",Intensity_best[i]," ",low_bound_68[i]," ",high_bound_68[i]," ",low_bound_95[i]," ",high_bound_95[i]


##****************PLOTTING**********************##


## Plot bounds in SED space

#lamb_new = np.linspace(1,915,900)
#lamb_new= np.logspace(np.log10(1),np.log10(1500),72, endpoint=True)
lamb_new= np.logspace(np.log10(1),np.log10(100),1000, endpoint=True)
high_bound_68_spline = spline(lamb,high_bound_68,lamb_new,order=1)
low_bound_68_spline = spline(lamb,low_bound_68,lamb_new,order=1)

high_bound_90_spline = spline(lamb,high_bound_90,lamb_new, order=1)
low_bound_90_spline = spline(lamb,low_bound_90,lamb_new, order=1)

high_bound_95_spline = spline(lamb,high_bound_95,lamb_new, order=1)
low_bound_95_spline = spline(lamb,low_bound_95,lamb_new, order=1)


fig, ax = plt.subplots(1)
legend = TLegend(0.1,0.8,0.4,0.9)

plt.ylim([1, 80])

ax.set_yscale('log')
ax.set_xscale('log')
#plt.title("Mrk501 - BPL - low -1$\sigma$")
#plt.title("Mrk501 - BPL - high +1$\sigma$")
#ax.text(0.5, 0.5, 'PRELIMINARY', transform=ax.transAxes,
#        fontsize=40, color='gray', alpha=0.5,
#        ha='center', va='center', rotation='30')


plt.title("Mrk 421 - ECPL - median")


#ax.set_yscale('log')
#ax.set_xscale('log')

ax.fill_between(lamb_new, high_bound_95_spline, low_bound_95_spline, facecolor='darkred', alpha=1, label='Containment band 95%',interpolate=True)
#ax.fill_between(lamb_new, high_bound_90_spline, low_bound_90_spline, facecolor='green', alpha=0.5, label='Agreement region 90%',interpolate=True)
ax.fill_between(lamb_new, high_bound_68_spline, low_bound_68_spline, facecolor='lightblue', alpha=1, label='Containment band 68%',interpolate=True)


##Add some standard EBL model
I_dom =  EBL.readmodel(model = 'dominguez')
I_fra =  EBL.readmodel(model = 'franceschini')

z = 0.031
lmu = np.logspace(-0.1,2,50)
Int_fra=I_fra.ebl_array(z,lmu)
Int_fra = Int_fra[0,:]
Int_dom=I_dom.ebl_array(z,lmu)
Int_dom = Int_dom[0,:]

plt.plot(lmu,Int_fra,label = 'Franceschini (2008)'.format(z), lw = 2, color='lime')
#plt.plot(lmu,Int_dom,label = 'Dominguez'.format(z), lw = 2, color='lime')



##Add the CHOSEN model
log10x = np.linspace(np.log10(1),np.log10(100),1000,endpoint=True)
x = 10.**log10x

eblModel = PyEBL.ebl(namewithdir_int, best_model_number)
#y = eblModel.eblSED(x)
#plt.loglog(x,y,linewidth=2., color='red', label = "Best agreement")

lamb_chop = lamb[:17]

y = eblModel.eblSED(lamb_chop)
plt.plot(lamb_chop,y,linestyle = 'None', marker='o',
     markerfacecolor='black', markersize=6, label = "Max. likelihood")



plt.ylabel("$\\nu I_{\\nu}$ [nW$\,$m$^{-2}$sr$^{-1}$]",fontsize=15)
plt.xlabel("$\lambda \, [\mu$m]",fontsize=15)
plt.show()


##Plot limits and VERITAS bands
f_up=open('/Users/mateo/Documents/HAWC/EBL/EBLmodel_likelihood/makeSplines/EBL_bound_extraction/upper_Limits_fromKrennrich_um_nWm2sr1.dat', 'r')
f_low=open('/Users/mateo/Documents/HAWC/EBL/EBLmodel_likelihood/makeSplines/EBL_bound_extraction/lower_Limits_fromKrennrich_um_nWm2sr1.dat', 'r')
f_both=open('/Users/mateo/Documents/HAWC/EBL/VERITAS_EBL/Data.csv', 'r')

lines_both=	f_both.readlines()
lamb_up_both=[]
int_up_both=[]
lamb_low_both=[]
int_low_both=[]
line_n=0
for x in lines_both:
	if (line_n % 2) == 0:
		if(1<float(x.split(' ')[0])<100):
	    		lamb_low_both.append(float(x.split(' ')[0]))
	    		int_low_both.append(float(x.split(' ')[1]))
	else:
		if(1<float(x.split(' ')[0])<100):
		   		lamb_up_both.append(float(x.split(' ')[0]))
		   		int_up_both.append(float(x.split(' ')[1]))
	line_n += 1
f_both.close()


lines_up=f_up.readlines()
lines_low=f_low.readlines()
lamb_up=[]
int_up=[]
lamb_low=[]
int_low=[]

for x in lines_up:
	if(1<float(x.split(' ')[0])<100):
    		lamb_up.append(float(x.split(' ')[0]))
    		int_up.append(float(x.split(' ')[1]))
f_up.close()

for x in lines_low:
	if(1<float(x.split(' ')[0])<100):
    		lamb_low.append(float(x.split(' ')[0]))
    		int_low.append(float(x.split(' ')[1]))
f_low.close()


plt.plot(lamb_low,int_low,'^',color='magenta',label='Lower Limits - Krennrich (2013)')
plt.plot(lamb_up,int_up,'v',color='lawngreen',label='Upper Limits - Krennrich (2013)')
#ax.fill_between(lamb_low,int_low_both , int_up_both, facecolor='green', alpha=0.5, label='VERITAS 95%',interpolate=True)

legend.Draw('same')


output_plot = os.path.join(path_to_weights_file,'SED_limits_ForPaper_ModColors.png')
ax.legend(loc=1, fontsize='x-small')
plt.savefig(output_plot)


## Plot histograms

fig2, ax2 = plt.subplots(1)
#legend = TLegend(0.2,0.8,0.3,0.9)
#legend = TLegend(.1,.7,.3,.9)
#print I_1

c0c = TCanvas("c0c","c0c",1800, 850)
gStyle.SetOptStat(0);

#c0c = ROOT.TCanvas("canvas")
legend = TLegend(.1,.7,.3,.9)
c0c.Divide(4,3)
c0c.SetLogx(1)
c0c.cd(1)
hist_array[0].Draw('h')
legend.AddEntry(graph_array[0],"68% containment region")
legend.Draw('same')
output_plot_2 = os.path.join(path_to_weights_file,'histograms.png')


for i in range(len(lamb)):


	#c0c.Draw()
	c0c.cd(i+1)
	gPad.SetLogx();
	legend = TLegend(.1,.7,.3,.9)
	legend.AddEntry(graph_array[0],"68% containment region")
	hist_array[i].GetXaxis().SetTitle("#nu I [nW m^{-2} s^{-1}]")
	hist_array[i].GetYaxis().SetTitle("arb. units")
	hist_array[i].GetYaxis().SetTitleSize(0.03)
	hist_array[i].GetYaxis().SetLabelSize(0.025)
	hist_array[i].GetYaxis().SetTitleOffset(1.87)
	#print low_bound_68[i]
	c0c.Update()

	line_low_array[i].SetLineColor(2)
	line_low_array[i].SetLineStyle(2)
	line_low_array[i].SetLineWidth(2)
	line_high_array[i].SetLineColor(2)
	line_high_array[i].SetLineStyle(2)
	line_high_array[i].SetLineWidth(2)
	line_MaxBin_array[i].SetLineColor(1)
	line_MaxBin_array[i].SetLineStyle(2)
	line_MaxBin_array[i].SetLineWidth(3)

	hist_array[i].Draw('h')
	graph_array[i].SetFillColorAlpha(1,1)
	graph_array[i].SetFillStyle(3004)
	graph_array[i].Draw('f')
	line_low_array[i].Draw('same')
	line_high_array[i].Draw('same')
	line_MaxBin_array[i].Draw('same')
	c0c.SaveAs(output_plot_2)
	#legend.Draw('same')


legend.AddEntry(graph_array[0],"68% containment region")
gStyle.SetOptStat(0);

output_plot_3 = os.path.join(path_to_weights_file,'histograms_selection_ForPaper_ModColors.png')
c1c = TCanvas("c0c","c0c",1800, 850)
#c0c = ROOT.TCanvas("canvas")

#c0c.Divide(4,3)

c1c.Divide(2,1)
c1c.SetLogx(1)
c1c.cd(1)
gStyle.SetOptStat(0)

gPad.SetLogx()
legend = TLegend(0.15,0.8,0.3,0.9)
legend.SetTextSize(0.03)
legend.SetBorderSize(0)
legend.AddEntry(graph_array[3],"68% containment region")
legend.AddEntry(line_MaxBin_array[3],"Intensity_{max.Likelihood}")
hist_array[3].Scale(1./hist_array[3].Integral())
hist_array[3].Draw('h')
graph_array[3].SetFillColorAlpha(2,0.8)
graph_array[3].SetFillStyle(3004)
graph_array[3].Draw('f')
line_low_array[3].Draw('same')
line_high_array[3].Draw('same')
line_MaxBin_array[3].Draw('same')
legend.Draw('same')
c1c.cd(2)
gStyle.SetOptStat(0)

gPad.SetLogx()
legend2 = TLegend(0.15,0.8,0.3,0.9)
legend2.SetTextSize(0.03)
legend2.SetBorderSize(0)
legend2.AddEntry(graph_array[6],"68% containment region")
legend2.AddEntry(line_MaxBin_array[3],"Intensity_{max.Like}",)
hist_array[6].Scale(1./hist_array[6].Integral())
hist_array[6].Draw('same')
graph_array[6].SetFillColorAlpha(2,0.8)
graph_array[6].SetFillStyle(3004)
graph_array[6].Draw('f')
line_low_array[6].Draw('same')
line_high_array[6].Draw('same')
line_MaxBin_array[6].Draw('same')
legend2.Draw('same')

c1c.SaveAs(output_plot_3)

#legend.AddEntry(graph_array[0],"68% containment region")
#output_plot_3 = os.path.join(path_to_weights_file,'histograms_selection_ForPaper.png')

#plt.plot(lamb,lamb)
#c0c.Draw()

#hist_array[3].Draw('h')
#output_plot_2 = os.path.join(path_to_weights_file,'histograms.png')
#c0c.SaveAs(output_plot_2)
#plt.savefig(output_plot_2)
#fig.show(block=True)
#plt.show()
