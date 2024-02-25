import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pandas as pd
from functools import partial
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from shapely.geometry import Point
from string import capwords 
from mapclassify import FisherJenks
from prettytable import PrettyTable
import warnings 

class AnalizadorDatosApp(QWidget):
    def __init__(self):
        super().__init__()

        self.green_box = QLabel(self)
        self.green_box.setStyleSheet("background-color: white;")
        self.green_box.setGeometry(0, 0, 2000, 2000)

        self.green_box = QLabel(self)
        self.green_box.setStyleSheet("background-color: #80BCBD;")
        self.green_box.setGeometry(0, 0, 405, 2000)

        self.df = None
        self.result_table = None  # Store the result table widget
        self.vehicle_checkboxes = []  # Store the checkboxes for vehicles

        self.btn_cargar = QPushButton('Cargar Archivo Excel', self)
        self.btn_cargar.clicked.connect(self.cargar_archivo)
        self.btn_cargar.setObjectName("btn_cargar")  # Assign object name for styling


        # Cargar la fuente descargada
        font_id = QFontDatabase.addApplicationFont("Rubik.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        
        # Establecer la fuente como la fuente predeterminada para toda la aplicación
        default_font = QFont(font_family)
        QApplication.instance().setFont(default_font)

        self.initUI()

    def initUI(self):
        btn_duracion = self.create_button('Tiempo de Viaje (Media y Máximo)', self.duracion_media_maxima)
        btn_velocidad = self.create_button('Velocidad (Media y Máxima)', self.velocidad_media_maxima)
        btn_excesos = self.create_button('Lista de Excesos de Velocidad', self.lista_excesos_velocidad)
        btn_espera = self.create_button('Tiempo de Espera Promedio', self.lista_excesos_velocidad)
        btn_destinos = self.create_button('Destinos mas frecuentes', self.ubicaciones)


        grid_layout = QGridLayout()
        self.btn_cargar.setGeometry(17, 50, 372, 42)
        btn_duracion.setGeometry(17, 100, 372, 42)
        btn_velocidad.setGeometry(17, 150, 372, 42)
        btn_excesos.setGeometry(17, 200, 372, 42)
        btn_espera.setGeometry(17, 250, 372, 42)
        btn_destinos.setGeometry(17, 300, 372, 42)


        # Agregar espaciadores verticales entre los botones
        for i in range(5):
            spacer_item = QSpacerItem(20, 70, QSizePolicy.Minimum, QSizePolicy.Fixed)
            grid_layout.addItem(spacer_item, i, 0)

        checkbox_frame = QFrame(self)

        layout = QVBoxLayout(checkbox_frame)
        for vehicle in self.vehicle_checkboxes:
            checkbox = QCheckBox(vehicle, self)
            layout.addWidget(checkbox)
            self.vehicle_checkboxes.append(checkbox)

        self.result_table = QTableWidget(self)
        self.result_table.setGeometry(435, 30, 1160, 960)
        self.result_table.setStyleSheet('''
            QTableWidget {
                background-color: white;
                border: 1px solid #d4d4d4;
            }
        ''')
        

        self.setLayout(grid_layout)

        self.setWindowTitle('Analizador de Datos')

        self.btn_cargar.setStyleSheet('''
            QPushButton {
                background-color: #80BCBD;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 18px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #F9F7C9;
                color: #545460;
            }
        ''')

        self.checkbox_todos = QCheckBox("Todos", self)
        self.checkbox_todos.stateChanged.connect(self.seleccionar_todos_vehiculos)
        self.checkbox_todos.setStyleSheet("QCheckBox::indicator {width: 15px; height: 15px; color: #ff0000;} QCheckBox {font-size: 16px;color: black;}")
        self.checkbox_todos.setGeometry(1630, 187, 100, 20)

        self.create_vehicle_checkboxes()

        # Agregar el widget de calendario
        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())  # Establecer fecha predeterminada
        locale = QLocale(QLocale.Spanish, QLocale.Spain)
        self.date_edit.setLocale(locale)
        self.date_edit.setGeometry(1630, 56, 245, 28)
        label_inicio = QLabel("Inicio", self)
        font1 = QFont()
        font1.setPointSize(10)
        label_inicio.setFont(font1)
        label_inicio.setGeometry(1630, 30, 360, 20)


        # Cambiar el color de la parte superior del calendario
        self.date_edit.setStyleSheet("font-size: 14px;" '''
            QCalendarWidget QAbstractItemView:disabled {
                color: #555555; /* Color de texto para elementos deshabilitados */
            }
            QCalendarWidget QToolButton {
                background-color: #2D9596; /* Color de fondo para los botones de navegación */
                color: white; /* Color del texto para los botones de navegación */

            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #2D9596; /* Color de fondo de la barra de navegación */
                color: white; /* Color del texto dentro de la barra de navegación */
            }
            QCalendarWidget QAbstractItemView:enabled:selected {
                background-color: #2D9596; /* Color de fondo para fechas seleccionadas */
                color: white; /* Color del texto para fechas seleccionadas */
            }
        ''')


        # Agregar el widget de calendario
        self.date_edit2 = QDateEdit(self)
        self.date_edit2.setCalendarPopup(True)
        self.date_edit2.setDate(QDate.currentDate())  # Establecer fecha predeterminada
        locale = QLocale(QLocale.Spanish, QLocale.Spain)
        self.date_edit2.setLocale(locale)
        self.date_edit2.setGeometry(1630, 126, 245, 28)
        label_inicio = QLabel("Final", self)
        font1 = QFont()
        font1.setPointSize(10)
        label_inicio.setFont(font1)
        label_inicio.setGeometry(1630, 100, 245, 20)


        # Cambiar el color de la parte superior del calendario
        self.date_edit2.setStyleSheet("font-size: 14px;" '''
            QCalendarWidget QAbstractItemView:disabled {
                color: #555555; /* Color de texto para elementos deshabilitados */
            }
            QCalendarWidget QToolButton {
                background-color: #2D9596; /* Color de fondo para los botones de navegación */
                color: white; /* Color del texto para los botones de navegación */

            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #2D9596; /* Color de fondo de la barra de navegación */
                color: white; /* Color del texto dentro de la barra de navegación */
            }
            QCalendarWidget QAbstractItemView:enabled:selected {
                background-color: #2D9596; /* Color de fondo para fechas seleccionadas */
                color: white; /* Color del texto para fechas seleccionadas */
            }
        ''')
        
    

    def create_button(self, text, callback):
        button = QPushButton(text, self)
        button.clicked.connect(partial(self.mostrar_resultado, callback))
        button.setStyleSheet('''
            QPushButton {
                background-color: #80BCBD;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 18px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #F9F7C9;
                color: #545460;
            }
        ''')
        return button

    def mostrar_resultado(self, funcion_analisis):
        if self.df is None:
            return

        # Filtrar el DataFrame según los vehículos seleccionados
        selected_vehicles = [checkbox.text() for checkbox in self.vehicle_checkboxes if checkbox.isChecked()]
        if not selected_vehicles:
            self.mostrar_mensaje("Debe seleccionar al menos un vehículo.")
            return

        # Filtrar por rango de fechas
        fecha_inicio = self.date_edit.date().toPyDate()
        fecha_fin = self.date_edit2.date().toPyDate()
        self.df['Start Date'] = pd.to_datetime(self.df['Start Date']).dt.date
        filtered_df = self.df[(self.df['Start Date'] >= fecha_inicio) & (self.df['Start Date'] <= fecha_fin)]

        if filtered_df.empty:
            self.mostrar_mensaje("No hay datos para el rango de fechas seleccionado.")
            return

        filtered_df = filtered_df[filtered_df['Device'].isin(selected_vehicles)]

        if not filtered_df.empty:
            if self.result_table:
                self.result_table.setParent(None)  # Remove the existing table

            resultado = funcion_analisis(filtered_df)  # Usar el DataFrame filtrado
            self.result_table = self.crear_tabla_resultados(resultado)
            self.result_table.setGeometry(435, 30, 1160, 960)  # Establecer la geometría de la tabla de resultados
            self.result_table.show()
        else:
            self.mostrar_mensaje("No hay resultados para los vehículos seleccionados en el rango de fechas especificado.")

        

    def duracion_media_maxima(self, df):
        # Filtro, valor mayor y media ABSOLUTO

        # El valor medio
        # Conversión de formato
        df['Driving Duration'] = pd.to_timedelta(df['Driving Duration'].astype(str))


        # Filtro, valor mayor y media UNIDAD
        # Obtener nombres sin repetir
        unique_devices = df['Device'].unique()

        # Automatización para cada TAP
        table_data = []
        for device in unique_devices:
            # Filtro para cada para TAP
            filtered_df = df.query('Device == @device')

            # Conversión del formato
            driving_durations_u = pd.to_timedelta(filtered_df['Driving Duration'].astype(str))

            # Media
            mean_duration_u = driving_durations_u.mean()

            # Máximo
            max_value_u = driving_durations_u.max()

            # Traducción
            max_value_un = str(max_value_u).replace(' days', ' días')
            mean_duration_un = str(mean_duration_u).replace(' days', ' días')

            # Guardar en la tabla de resultados
            table_data.append({'Vehículo': device, 'Duración Media': mean_duration_un, 'Duración Máxima': max_value_un})

        # Crear el DataFrame con los resultados
        df_table = pd.DataFrame(table_data)

        # Ordenar el DataFrame por la columna 'Device'
        df_table = df_table.sort_values(by='Vehículo')

        return df_table

    def velocidad_media_maxima(self, df):
        # Rapidez por unidad y absoluto

        # Filtro, valor mayor y media UNIDAD
        # Obtener nombres sin repetir
        unique_devices = df['Device'].unique()

        # Automatización para cada TAP
        table_data = []
        for device in unique_devices:
            # Filtro para cada para TAP
            filtered_dff = df.query('Device == @device')
            # Media
            mean_speed_u = filtered_dff['Maximum Speed'].mean()
            # Máximo
            max_speed_u = filtered_dff['Maximum Speed'].max()
            # Guardar en la tabla de resultados
            table_data.append({'Vehículo': device, 'Velocidad Media': mean_speed_u, 'Velocidad Máxima': max_speed_u})

        # Crear el DataFrame con los resultados
        df_table = pd.DataFrame(table_data)

        # Ordenar el DataFrame por la columna 'Device'
        df_table = df_table.sort_values(by='Vehículo')

        return df_table

    def lista_excesos_velocidad(self, df):
        max_speed_df = df[df['Maximum Speed'] > 120]
        filtered_data = max_speed_df[['Device', 'Start Date', 'Stop Date', 'Maximum Speed']]
        
        # Renombrar las columnas
        filtered_data.columns = ['Vehículo', 'Inicio', 'Final', 'Velocidad máxima']

        return filtered_data
        
    def ubicaciones(self,df):
        GeoJson='Distritos_de_Costa_Rica.geojson'
        #abrimos el GEojson y creamos un dataframe con los distritos
        CR=gpd.read_file(GeoJson)
        CR=CR.drop(['OBJECTID', 'COD_PROV', 'COD_CANT', 'COD_DIST', 'CODIGO'],axis=1)
        CR=CR.drop(678)# #La fila 678 no tiene nada, debe ser un error del archivo
        CR=CR.reset_index(drop=True)
        #=CR.drop(columns=["index"])#le arreglamos el indice despues de usar drop

        points=df.apply(lambda fila: Point(fila.TripDetailLongitude, fila.TripDetailLatitude),axis=1)

        #checamos en qué distrito se hizo cada viaje
        trips_df = gpd.GeoDataFrame(geometry=points,crs=4326)

        CANTIDAD_DE_VIAJES = []
        for dist in CR['geometry']:
            trip = None
            trip = trips_df[trips_df.geometry.within(dist)]
            CANTIDAD_DE_VIAJES.append(len(trip))
            
        CR['CANTIDAD_DE_VIAJES']=CANTIDAD_DE_VIAJES
        niveles=None
        if len(CR['CANTIDAD_DE_VIAJES'].unique())>=5:
            niveles=5
        else:
            niveles=len(CR['CANTIDAD_DE_VIAJES'].unique())

        sch=FisherJenks(CR['CANTIDAD_DE_VIAJES'],k=niveles)
        #ordenamospor niveles
        limites=sch.bins.tolist()#limites de los niveles

        CR_ordenado=CR.sort_values(by='CANTIDAD_DE_VIAJES',ascending=False)
        CR_ordenado.reset_index(drop=True, inplace=True)
        if len(limites)>=4:#por si los datos no variaran tanto
            CR_ordenado=CR_ordenado[CR_ordenado['CANTIDAD_DE_VIAJES']>limites[-4]]
        #imprimimos los 3 primeros niveles de ordenamiento
        CR_ordenado.index += 1
        CR_ordenado.drop(['ID', 'geometry'],axis=1, inplace=True)
        CR_ordenado.reset_index(inplace=True)
        CR_ordenado=CR_ordenado.rename(columns={"index": "Puesto",
                              "NOM_PROV": "Provincia",
                              "NOM_CANT":"Canton",
                                 "NOM_DIST":"Distrito",
                                 "CANTIDAD_DE_VIAJES":"Cantidad de viajes"})
                
    ####### para hacer la imagen
        fig, axis = plt.subplots()
        CR.plot(cmap='Accent',edgecolor='black',linewidth=0.35,
                      column='CANTIDAD_DE_VIAJES',scheme='FisherJenks',
                      k=niveles,legend=True, ax=axis,
                      legend_kwds={"loc": "lower left","interval": True})
        
        axis.set_axis_off()
        
        plt.ylim(7.7, 11.5)
        plt.xlim(-86, -82.5)
        line="Destino más visitado:\n{}, {}, {}".format(capwords(CR_ordenado.at[0,'Distrito']),
                                                        capwords(CR_ordenado.at[0,'Canton']),
                                                        capwords(CR_ordenado.at[0,'Provincia']))
        bbox = dict(boxstyle ="round", fc ="1",ec="0.7") 
        plt.annotate(line, xy =(-83,11),xytext =(-86,11.5),
                      color='black',fontsize = 10, bbox=bbox)
        plt.show()
        # canvas=FigureCanvasQTAgg(fig)
        # layout.addWidget(canvas)
        
        return CR_ordenado

    def crear_tabla_resultados(self, result_data):
        table_widget = QTableWidget(self)
        table_widget.setRowCount(result_data.shape[0])
        table_widget.setColumnCount(result_data.shape[1])

        for i in range(result_data.shape[1]):
            header_item = QTableWidgetItem(result_data.columns[i])
            table_widget.setHorizontalHeaderItem(i, header_item)

        for i in range(result_data.shape[0]):
            for j in range(result_data.shape[1]):
                item = QTableWidgetItem(str(result_data.iloc[i, j]))
                table_widget.setItem(i, j, item)

        # Resize columns to content
        table_widget.resizeColumnsToContents()

        # Set horizontal header resizing to stretch
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        table_widget.setStyleSheet('''
            QTableWidget {
                background-color: white;
                alternate-background-color: #f2f2f2;
                selection-background-color: #F9F7C9;
                selection-color: #545460;
                border: 1px solid #d4d4d4;
            }
        ''')

        return table_widget

    def cargar_archivo(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Archivos Excel (*.xlsx)")
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                self.df = cargar_datos(file_path)
                self.btn_cargar.setText(f"{file_path.split('/')[-1]} cargado")
                self.setWindowTitle(f'Analizador de Datos - {file_path.split("/")[-1]}')
                self.mostrar_mensaje(f"{file_path} cargado")
                self.create_vehicle_checkboxes()  # Create vehicle checkboxes

    def mostrar_mensaje(self, mensaje):
        QMessageBox.information(self, 'Información', mensaje)

    def create_vehicle_checkboxes(self):
        if self.df is None:
            return

        # Remove existing checkboxes
        for checkbox in self.vehicle_checkboxes:
            checkbox.setParent(None)

        # Get unique vehicle names
        unique_vehicles = self.df['Device'].unique()

        # Create checkboxes for each vehicle
        layout = QVBoxLayout()

        spacer_item_top = QSpacerItem(20, 60, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(spacer_item_top)

        for vehicle in unique_vehicles:
            checkbox = QCheckBox(vehicle, self)
            checkbox.setStyleSheet("QCheckBox::indicator {width: 15px; height: 15px;} QCheckBox {font-size: 16px; margin-left: 1594px; color: black;}")
            layout.addWidget(checkbox)
            self.vehicle_checkboxes.append(checkbox)

        # Add the checkboxes to the right side of the layout
        self.layout().addLayout(layout, 0, 1, 1, 1)
    


    def seleccionar_todos_vehiculos(self, state):
        # Change the state of all vehicle checkboxes
        for checkbox in self.vehicle_checkboxes:
            checkbox.setChecked(state == Qt.Checked)
            

def cargar_datos(file_path):
    df = pd.read_excel(file_path, sheet_name='Report', skiprows=range(0, 11))
    row_0 = df.iloc[0].tolist()
    df.columns = row_0
    df = df.drop(df.index[0])
    return df

def main():
    app = QApplication(sys.argv)
    ex = AnalizadorDatosApp()
    ex.showMaximized()  # Show the window maximized
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
