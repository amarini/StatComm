#Unfolding with Combine

## General introduction

Many books and chapters have been written about it, and these three lines do not certainly fully describe the problem. 
[bib1] TODO

### What is unfolding 
Unfolding or usmearing is the ``art'' of undo detector induced smearing effects, 
in order to bring the observation to a prior theory level.

https://www.codecogs.com/eqnedit.php?latex=\mathcal{W}(A,f)&space;=&space;(T,\bar{f})

Basic idea behind unfolding techniques is linearity, i.e., the possibility of describing 
changes induced by the detector in the truth bin $x_i$ through a linear relation of what happens 
in the nearby truth-bins. Or in other words that we can model through probability p_j (independent of e.g. the content) 
the changes that the event falling in the truth bin x_i is reconstructed in the bin y_j (p_j=\tilde{R}_{ij})

$$ y_\textup{obs} =  \mathbf{\tilde{R}} \cdot x_\textup{true} + b $$

Or, if R contains the expected yields with respect to a particular mc. We will use this formalism.
$$ y_\textup{obs} =  \mathbf{R} \cdot \mu + b $$

Unfolding aims to find the truth distribution x, given the observation y.

###Regularization

The problem 

### Avaialable software
There are many software tools to perform unfolding and each of them as pro and contra.
* RooUnfold. Extension to ROOT, simple to use, can easily switch across regularization types
* TUnfold. Embedded in ROOT.

## Using combine tool to perform unfolding

Why ? 
* because we want, because we can
* because background subtraction/signal extraction are non trivial
* because nuisances and correlations are non trivial 
* because we want to profile nuisances ...

## How

Simple case w/o regularization
### Write the likelihood function

Combine minimize the likelihood function for you. 
Given the true content induced by the bin $i$, the expected events for the true-bin $i$ in the reco-bin $j$.
and P is the poisson distribution/likelihood:

$$ L= \prod_j \mathcal{P}(y_j|\Sum_i x_i R_ij + b_j) $$

Not that is complex extraction through ancillary variables indexed trough k (e.g. invariant mass of something):
$$ L = \prod_j \prod_k \mathcal{P}(y_jk| \Sum_i x_ik Rijk + b_j) $$ (TO CHECK)

Given the true spectrum with the same MC x_true, the observations are now, remembering that R includes corrected efficiency and acceptance factors:
$$ x_obs = x_true * mu_obs $$

Nuisances can be added to the likelihood function and profiled in the usual way.

### with regularization

Unfolding with regularization in combine is a bit tricky and very-experimental
It is based on this PR to combine:

https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit/pull/331

In case of using SVD regularization as in RooUnfold, nuisance lines such as:
~~~
constr1 constr const1_In[0.],RooFormulaVar::fconstr1("r_Bin0+r_Bin2-2*r_Bin1",{r_Bin0,r_Bin1,r_Bin2}),delta[0.03]
constr2 constr const2_In[0.],RooFormulaVar::fconstr2("r_Bin1+r_Bin3-2*r_Bin2",{r_Bin1,r_Bin2,r_Bin3}),delta[0.03]
constr3 constr const3_In[0.],RooFormulaVar::fconstr3("r_Bin2+r_Bin4-2*r_Bin3",{r_Bin2,r_Bin3,r_Bin4}),delta[0.03]
~~~

In case of using TUnfold like regularization (more complicate, need to have access to the gen content in each bin through the normalization.
Each bin must therefore been implemented separately, and not using histograms to simplify the summing over one dimension:

~~~
constr1 constr const1_In[0.],RooFormulaVar::fconstr1("(r_Bin0-1.)*(GenBin0_RecoBin0_norm+GenBin0_RecoBin1_norm+GenBin0_RecoBin2_norm+GenBin0_RecoBin3_norm+GenBin0_RecoBin4_norm)+r_Bin2*(GenBin12_RecoBin0_norm+GenBin12_RecoBin1_norm+GenBin12_RecoBin2_norm+GenBin12_RecoBin3_norm+GenBin12_RecoBin4_norm)-2*r_Bin1*(GenBin1_RecoBin0_norm+GenBin1_RecoBin1_norm+GenBin1_RecoBin2_norm+GenBin1_RecoBin3_norm+GenBin1_RecoBin4_norm)",{r_Bin0,r_Bin1,r_Bin2,GenBin1_RecoBin0_norm,GenBin0_RecoBin0_norm,GenBin12_RecoBin0_norm,GenBin1_RecoBin1_norm,GenBin0_RecoBin1_norm,GenBin12_RecoBin1_norm,GenBin1_RecoBin2_norm,GenBin0_RecoBin2_norm,GenBin12_RecoBin2_norm,GenBin1_RecoBin3_norm,GenBin0_RecoBin3_norm,GenBin12_RecoBin3_norm,GenBin1_RecoBin4_norm,GenBin0_RecoBin4_norm,GenBin12_RecoBin4_norm}),delta[0.03]
constr2 constr const2_In[0.],RooFormulaVar::fconstr2("(r_Bin1-1.)*(GenBin1_RecoBin0_norm+GenBin1_RecoBin1_norm+GenBin1_RecoBin2_norm+GenBin1_RecoBin3_norm+GenBin1_RecoBin4_norm)+r_Bin3*(GenBin13_RecoBin0_norm+GenBin13_RecoBin1_norm+GenBin13_RecoBin2_norm+GenBin13_RecoBin3_norm+GenBin13_RecoBin4_norm)-2*r_Bin2*(GenBin2_RecoBin0_norm+GenBin2_RecoBin1_norm+GenBin2_RecoBin2_norm+GenBin2_RecoBin3_norm+GenBin2_RecoBin4_norm)",{r_Bin1,r_Bin2,r_Bin3,GenBin2_RecoBin0_norm,GenBin1_RecoBin0_norm,GenBin13_RecoBin0_norm,GenBin2_RecoBin1_norm,GenBin1_RecoBin1_norm,GenBin13_RecoBin1_norm,GenBin2_RecoBin2_norm,GenBin1_RecoBin2_norm,GenBin13_RecoBin2_norm,GenBin2_RecoBin3_norm,GenBin1_RecoBin3_norm,GenBin13_RecoBin3_norm,GenBin2_RecoBin4_norm,GenBin1_RecoBin4_norm,GenBin13_RecoBin4_norm}),delta[0.03]
constr3 constr const3_In[0.],RooFormulaVar::fconstr3("(r_Bin2-1.)*(GenBin2_RecoBin0_norm+GenBin2_RecoBin1_norm+GenBin2_RecoBin2_norm+GenBin2_RecoBin3_norm+GenBin2_RecoBin4_norm)+r_Bin4*(GenBin14_RecoBin0_norm+GenBin14_RecoBin1_norm+GenBin14_RecoBin2_norm+GenBin14_RecoBin3_norm+GenBin14_RecoBin4_norm)-2*r_Bin3*(GenBin3_RecoBin0_norm+GenBin3_RecoBin1_norm+GenBin3_RecoBin2_norm+GenBin3_RecoBin3_norm+GenBin3_RecoBin4_norm)",{r_Bin2,r_Bin3,r_Bin4,GenBin3_RecoBin0_norm,GenBin2_RecoBin0_norm,GenBin14_RecoBin0_norm,GenBin3_RecoBin1_norm,GenBin2_RecoBin1_norm,GenBin14_RecoBin1_norm,GenBin3_RecoBin2_norm,GenBin2_RecoBin2_norm,GenBin14_RecoBin2_norm,GenBin3_RecoBin3_norm,GenBin2_RecoBin3_norm,GenBin14_RecoBin3_norm,GenBin3_RecoBin4_norm,GenBin2_RecoBin4_norm,GenBin14_RecoBin4_norm}),delta[0.03]
~~~
