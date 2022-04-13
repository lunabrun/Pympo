%% Project: MHH Dissertation
%  Title/File: DamageJanececk2015.m
%  Author: Bruno Luna 
%  Date (start): 07 August 2021
%
%  Content
%  ------------
% 
%  This file contains code for calculation of damage on titanium based on paper
%  from Janececk2015. It shall be one of the possibilities for functions to be
%  called for the "actual" damage function.
%
%  Main assumptions:
%  1 - Constant cycle load (i.e., "sinus"-like load curve)
%  2 - SN curve with as a single segment (no "knee")
%  3 - All calculations valid for the input load range only
%  4 - Surely many others (model still VERY simplistic)
%  5 - Curve originally obtained for fully reversed (R=-1) case!
%

function N = DamageJanececk2015(S);
  
%% Hard-code the parameters obtained in curve fitting (see paper Janaceck2015)
a = 1700;             % Parameter of Basquin function (MPa)
B = -4900;            % Extension using Stromeyer function
b = -0.2;             % Parameter of Basquin function (admin)
Sinf = 440;           % Permanent fatigue limit (MPa) - Palmgreen extension
% Extra parameter
Sult = 1050;           % Ultimate stress (MPa) - Value from Janececk2015
                       % Missing low cycle fatigue area!

if (S < Sinf)
  N = 10^16; % Infinity life for all pratical purposes
elseif (S> Sult)      % CHECK THIS CONDITION! MISSING LOW FATIGUE AREA
  N = 1;      % One cycle ultimate stress amplitude is enough to cause failure
else
  N = ((S-Sinf)/a).^(1/b) - B; % Number of cycles for failure with this stress
endif

endfunction

%% For testing/debugging only
##%% Calculation using Palmgreen function (extension of Basquin)
##N = logspace(4,10);
##S = a*(N + B).^b + Sinf; % Fatigue stress for number of cycles
##
##%% Comparison from fig. 2 of Janececk2015 (values taken "by hand" from figure)
##Np = [10^4 10^5 10^6 10^7 10^8 10^9 10^10];
##Sp = [720 590 530 500 475 460 452];
##
##%% Plot
##figure;
##hold on 
##semilogx(N,S,'k', "linewidth", 2.0)
##semilogx(Np,Sp,'r-x', "linewidth", 2.0)
##ylim([400 900])        % Set plot range for stresses (MPa)
##xlim([3*10^3 2*10^10]) % Set plot range for cycles (admin)
##xlabel ("N (Number of cycles)");
##ylabel ("S (Stress Amplitude - MPa)");
##title ("S-N Curve of Ti-6Al-4V Alloy");
## legend ({"Palmgreen Eq.", "Curve from Fig.2 of (Janececk2015)"});

