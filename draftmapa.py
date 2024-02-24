import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from string import capwords 
from mapclassify import FisherJenks
from prettytable import PrettyTable
import warnings 

excel='Advanced Default Trips Detail Report_20240208_203539.xlsx'

GeoJson='Distritos_de_Costa_Rica.geojson'
#abrimos el GEojson y creamos un dataframe con los distritos
CR=gpd.read_file(GeoJson)
CR=CR.drop(['OBJECTID', 'COD_PROV', 'COD_CANT', 'COD_DIST', 'CODIGO'],axis=1)
CR=CR.drop(678)# #La fila 678 no tiene nada, debe ser un error del archivo
CR=CR.reset_index(drop=True)
#=CR.drop(columns=["index"])#le arreglamos el indice despues de usar drop

#leemos el excel y lo ponemos en df
df = pd.read_excel(excel, skiprows = 10, usecols =['TripDetailLatitude',
'TripDetailLongitude'])
points=df.apply(lambda fila: Point(fila.TripDetailLongitude, fila.TripDetailLatitude),axis=1)


#checamos en qué distrito se hizo cada viaje
trips_df = gpd.GeoDataFrame(geometry=points,crs=4326)

CANTIDAD_DE_VIAJES = []
for dist in CR['geometry']:
    trip = None
    trip = trips_df[trips_df.geometry.within(dist)]
    CANTIDAD_DE_VIAJES.append(len(trip))
    
CR['CANTIDAD_DE_VIAJES']=CANTIDAD_DE_VIAJES
sch=FisherJenks(CR['CANTIDAD_DE_VIAJES'])#ordenamospor niveles
limites=sch.bins.tolist()#limites de los niveles

CR_ordenado=CR.sort_values(by='CANTIDAD_DE_VIAJES',ascending=False)
CR_ordenado.reset_index(drop=True, inplace=True)
if len(limites)>=4:#por si los datos no variaran tanto
    CR_ordenado=CR_ordenado[CR_ordenado['CANTIDAD_DE_VIAJES']>limites[-4]]
#imprimimos los 3 primeros niveles de ordenamiento
CR_ordenado.index += 1
CR_ordenado.drop(['ID', 'geometry'],axis=1, inplace=True)
CR_ordenado.reset_index(inplace=True)

####### para hacer la tabla
def tabla(CR,CR_ordenado):
    print("Destinos más visitados:")
    table = PrettyTable()
    table.field_names = ["Puesto","Provincia", "Cantón", "Distrito", "Cantidad de viajes"]
    
    # Añadir las filas al DataFrame
    for i in range(CR_ordenado.shape[0]):
        table.add_row(CR_ordenado.iloc[i].tolist())
    
    print(table)  
            
####### para hacer la imagen
def imagen(CR, CR_ordenado):
    axis=CR.plot(cmap='Accent',edgecolor='black',linewidth=0.35,
                  column='CANTIDAD_DE_VIAJES',scheme='FisherJenks',
                  legend=True, 
                  legend_kwds={"loc": "lower left","interval": True})
    
    axis.set_axis_off()
    
    plt.ylim(7.7, 11.5)
    plt.xlim(-86, -82.5)
    line="Destino más visitado:\n{}, {}, {}".format(capwords(CR_ordenado.at[0,'NOM_DIST']),
                                                    capwords(CR_ordenado.at[0,'NOM_CANT']),
                                                    capwords(CR_ordenado.at[0,'NOM_PROV']))
    bbox = dict(boxstyle ="round", fc ="1",ec="0.7") 
    plt.annotate(line, xy =(-83,11),xytext =(-86,11.5),
                  color='black',fontsize = 10, bbox=bbox)
    plt.show()


#le pongo esto porque sino me dice que instale Numba para más rapidez

warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')
tabla(CR,CR_ordenado)
imagen(CR, CR_ordenado)
    
