Cooper Koers
12/13/2024
AAS350
GeoFlux: Simulating Migratory Patterns of American Cities











This paper represents my own work in accordance with University regulations.
/s/ Cooper Koers /s/

Background
Context:
American cities are dynamic entities regarding racial makeup in a geographic sense. City centers in before the Great Migration consisted largely of White European population; but, with the influx of rural Black Southerners fleeing the South for greater opportunity, many of these city centers became predominantly Black as White people fled in masses in an event known as White Flight. Yet, in recent years there has been a new phenomenon – gentrification. There has been a reversal of White Flight in which White people are moving back into city centers in droves, in turn hiking up housing costs and driving extant communities out into the areas originally founded as suburbs. This trend was the inspiration in large part behind my choice of AAS 350. In my home city of Indianapolis, this has been on display in large part on the city’s northside – resulting in a displacement of Indianapolis’s historic Black communities on the near west and east sides. Curious to the root causes of this, I explored how race relationships can be modelled in a statistical lens to result in familiar patterns of population composition change. Combining my loves of computer programming and population statistics, I modeled how the combination of White Flight and gentrification emerges in a software called GeoFlux. GeoFlux models population shifts of cities given a set of parameters and outputs plots of cities at time steps, such that the user can observe population structure trends as they evolve. 
Software Availability:
GeoFlux is available at https://geoflux.streamlit.app, with source code available at https://github.com/cooperkoers/GeoFlux

Modeling
Theoretical Model:
The basis of the model lies in the race relationships between neighbors. Each family in the model is designated with a race attribute: majority or minority. The tags majority and minority were decided upon in the case that the project expand into cities across other continents, where the nomenclature of White and Black are not necessarily applicable. Given their neighbors, the model determines a direction in which it believes the family will move at the next time step. In this model, majority races are attracted toward other members of majority races and repelled by neighbors of minority races. Families of minority races experience slight attraction toward both members of majority and minority races. These interactions help to model White Flight in American cities. Every family additionally experiences attraction toward city centers. The parameters designed in the model allow for this relationship to eventually develop into majority race movement trends into the inner cities, thus modeling gentrification.
Mathematical Model:
The model is based around the concept of a stochastic vector field. The interaction between each family and its neighbor is defined by a single directional vector, where the direction of this vector is dependent upon the race relationship. Each vector then undergoes an inverse square law transformation such that neighbors closer to the family have a greater effect on the outcome. Each effect vector is then summed to result in a total effect vector. This vector then undergoes random sampling under a normal distribution. This allows for stochasticity in the movement of each family. Each neighbor effect vector is summed and then added to a calculated centroid vector that points to the centroid of the city shape. This end vector is the direction in which the family will move.
Race relations are modelled using the following matrix R:
\begin{matrix}.&majority\ neighbor&minority\ neighbor\\majority\ family&0.0001&-0.001\\minority\ family&0.00005&0\\\end{matrix}
The effect vector of each neighbor on the family of interest is calculated from the following equation:
\bar{e_i}=fx-px,fy-py(fx-px)2+ (fy-py)2
Where:
f_x=The\ latitude\ of\ the\ family
f_y=The\ longitude\ of\ the\ family
p_x=The\ latitude\ of\ the\ neighbor
p_y=The\ latitude\ of\ the\ neighbor
The direction effect vector is given by the following equation:
\bar{d_i}=\frac{1}{{(\sqrt{{{(f}_x-p_x)}^2+\ {{(f}_y-p_y)}^2})}^2}
The final transformed vector for each neighbor on a family is given by the following equation:
\bar{p_i}=R_{r_f,r_n}\cdot\bar{e_i}\cdot\bar{d_i}+\mathcal{N}\left(0,{0.05}^2\right)

Where:
r_f=race\ of\ the\ family
r_n=race\ of\ the\ neighbor
\mathcal{N}\left(0,{0.05}^2\right)\ =\ Normal\ Gaussian\ distribution\ centered\ around\ 0\ with\ covariance\ 0.05
The vector for the pull toward the city centroid is modelled by the following equation:
\bar{c}=0.01\bullet\sqrt{{{(f}_x-c_x)}^2+\ {{(f}_y-c_y)}^2}
Finally, the vector of a family is calculated by the following equation:
\bar{v}\ =\bar{c}+\ \sum_{i=0}^{n}\left(p_i\right)
Functionality
GeoFlux allows users to model both White Flight and gentrification in American cities of their choosing. 


![image](https://github.com/user-attachments/assets/17d265a1-6dd5-4756-8aa1-f88c902ad63a)
