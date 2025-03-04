import json
import os
from datetime import datetime

class SistemaEstadisticasGlobales:
    def __init__(self):
        
        self.indicadores = self._cargar_json('indicadores.json')
        self.paises = self._cargar_json('paises.json')
        self.poblacion = self._cargar_json('poblacion.json')
    
    def _cargar_json(self, nombre_archivo):
        
        try:
            with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
                return json.load(archivo)
        except FileNotFoundError:
            print(f"Advertencia: El archivo {nombre_archivo} no fue encontrado. Se inicializará vacío.")
            return []
        except json.JSONDecodeError:
            print(f"Error: El archivo {nombre_archivo} no contiene JSON válido.")
            return []
    
    def _guardar_json(self, datos, nombre_archivo):
        
        with open(nombre_archivo, 'w', encoding='utf-8') as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)
    
    def agregar_dato_poblacion(self, año, pais, indicador_id, valor, estado="disponible", unidad="personas"):
        
        
        codigo_iso3 = None
        for p in self.paises:
            if p["nombre"] == pais:
                codigo_iso3 = p["codigo_iso3"]
                break
        
        if not codigo_iso3:
            print(f"Error: País '{pais}' no encontrado.")
            return False
        
        descripcion_indicador = None
        for ind in self.indicadores:
            if ind["id_indicador"] == indicador_id:
                descripcion_indicador = ind["descripcion"]
                break
        
        if not descripcion_indicador:
            print(f"Error: Indicador '{indicador_id}' no encontrado.")
            return False
        
        for i, dato in enumerate(self.poblacion):
            if (dato["ano"] == año and 
                dato["codigo_iso3"] == codigo_iso3 and 
                dato["indicador_id"] == indicador_id):
                
                self.poblacion[i]["valor"] = valor
                self.poblacion[i]["estado"] = estado
                self.poblacion[i]["unidad"] = unidad
                self._guardar_json(self.poblacion, 'poblacion.json')
                return True
        
        nuevo_dato = {
            "ano": año,
            "pais": pais,
            "codigo_iso3": codigo_iso3,
            "indicador_id": indicador_id,
            "descripcion": descripcion_indicador,
            "valor": valor,
            "estado": estado,
            "unidad": unidad
        }
        
        self.poblacion.append(nuevo_dato)
        self._guardar_json(self.poblacion, 'poblacion.json')
        return True
    
    def agregar_pais(self, nombre, codigo_iso, codigo_iso3):
        
        
        for pais in self.paises:
            if pais["codigo_iso3"] == codigo_iso3:
                print(f"Error: Ya existe un país con el código ISO3 '{codigo_iso3}'.")
                return False
        
        nuevo_pais = {
            "nombre": nombre,
            "codigo_iso": codigo_iso,
            "codigo_iso3": codigo_iso3
        }
        
        self.paises.append(nuevo_pais)
        self._guardar_json(self.paises, 'paises.json')
        return True
    
    def agregar_indicador(self, id_indicador, descripcion):
        
        
        for indicador in self.indicadores:
            if indicador["id_indicador"] == id_indicador:
                print(f"Error: Ya existe un indicador con el ID '{id_indicador}'.")
                return False
        
        nuevo_indicador = {
            "id_indicador": id_indicador,
            "descripcion": descripcion
        }
        
        self.indicadores.append(nuevo_indicador)
        self._guardar_json(self.indicadores, 'indicadores.json')
        return True
    
    def obtener_datos_poblacion_pais(self, pais, año_inicio, año_fin):
        
        resultados = []
        
        for dato in self.poblacion:
            if (dato["pais"] == pais and 
                año_inicio <= dato["ano"] <= año_fin):
                resultados.append(dato)
        
        return resultados
    
    def calcular_crecimiento_poblacional(self, pais, año_inicio, año_fin):
        """Calcula el crecimiento poblacional año a año para un país"""
        
        datos_poblacion = []
        for dato in self.poblacion:
            if (dato["pais"] == pais and 
                año_inicio <= dato["ano"] <= año_fin and
                dato["indicador_id"] == "SP.POP.TOTL"):
                datos_poblacion.append(dato)
        
        datos_poblacion.sort(key=lambda x: x["ano"])
        
        resultados = []
        for i in range(1, len(datos_poblacion)):
            año_actual = datos_poblacion[i]["ano"]
            pob_actual = datos_poblacion[i]["valor"]
            pob_anterior = datos_poblacion[i-1]["valor"]
            
            crecimiento_absoluto = pob_actual - pob_anterior
            crecimiento_porcentual = (crecimiento_absoluto / pob_anterior) * 100 if pob_anterior > 0 else 0
            
            resultados.append({
                "año": año_actual,
                "poblacion": pob_actual,
                "crecimiento_absoluto": crecimiento_absoluto,
                "crecimiento_porcentual": round(crecimiento_porcentual, 2)
            })
        
        return resultados
    
    def listar_paises(self):
        
        return self.paises
    
    def obtener_datos_por_indicador(self, indicador_id):
        
        return [dato for dato in self.poblacion if dato["indicador_id"] == indicador_id]
    
    def obtener_datos_ultimos_años(self, num_años):
        
        
        if not self.poblacion:
            return []
        
        año_máximo = max(dato["ano"] for dato in self.poblacion)
        año_inicio = año_máximo - num_años + 1  
        
        return [dato for dato in self.poblacion if dato["ano"] >= año_inicio]
    
    def obtener_poblacion_pais_año(self, pais, año):
        
        for dato in self.poblacion:
            if (dato["pais"] == pais and 
                dato["ano"] == año and 
                dato["indicador_id"] == "SP.POP.TOTL"):
                return dato["valor"]
        
        return None
    
    def obtener_poblacion_antes_año(self, año):
        
        return [dato for dato in self.poblacion 
                if dato["ano"] < año and dato["indicador_id"] == "SP.POP.TOTL"]
    
    def obtener_poblacion_despues_año(self, año):
        
        return [dato for dato in self.poblacion 
                if dato["ano"] > año and dato["indicador_id"] == "SP.POP.TOTL"]
    
    def calcular_porcentaje_crecimiento(self, pais, año_inicio, año_fin):
        
        pob_inicio = self.obtener_poblacion_pais_año(pais, año_inicio)
        pob_fin = self.obtener_poblacion_pais_año(pais, año_fin)
        
        if pob_inicio is None or pob_fin is None:
            return None
        
        crecimiento = ((pob_fin - pob_inicio) / pob_inicio) * 100
        return round(crecimiento, 2)
    
    def obtener_año_poblacion_minima(self, pais):
        
        datos_pais = [dato for dato in self.poblacion 
                     if dato["pais"] == pais and dato["indicador_id"] == "SP.POP.TOTL"]
        
        if not datos_pais:
            return None
        
        return min(datos_pais, key=lambda x: x["valor"])["ano"]
    
    def contar_registros_por_año(self):
        
        conteo = {}
        for dato in self.poblacion:
            año = dato["ano"]
            conteo[año] = conteo.get(año, 0) + 1
        
        return conteo
    
    def paises_crecimiento_mayor(self, porcentaje, num_años):
        
        
        if not self.poblacion:
            return []
        
        año_máximo = max(dato["ano"] for dato in self.poblacion)
        año_inicio = año_máximo - num_años + 1
        
        resultados = []
        
        for pais in self.paises:
            nombre_pais = pais["nombre"]
            
            crecimiento = self.calcular_crecimiento_poblacional(nombre_pais, año_inicio, año_máximo)
            
            if crecimiento:
                crecimiento_promedio = sum(dato["crecimiento_porcentual"] for dato in crecimiento) / len(crecimiento)
                
                if crecimiento_promedio > porcentaje:
                    resultados.append({
                        "pais": nombre_pais,
                        "crecimiento_promedio": round(crecimiento_promedio, 2)
                    })
        
        return resultados
    
    def años_poblacion_mayor(self, pais, umbral):
        
        return [dato["ano"] for dato in self.poblacion 
                if dato["pais"] == pais and 
                   dato["indicador_id"] == "SP.POP.TOTL" and 
                   dato["valor"] > umbral]
    
    def obtener_poblacion_total_año(self, año):
        
        datos_año = [dato for dato in self.poblacion 
                    if dato["ano"] == año and dato["indicador_id"] == "SP.POP.TOTL"]
        
        return sum(dato["valor"] for dato in datos_año)
    
    def obtener_poblacion_minima_periodo(self, pais, num_años):
        
        
        if not self.poblacion:
            return None
        
        año_máximo = max(dato["ano"] for dato in self.poblacion)
        año_inicio = año_máximo - num_años + 1
        
        datos_periodo = [dato for dato in self.poblacion 
                        if dato["pais"] == pais and 
                           año_inicio <= dato["ano"] <= año_máximo and
                           dato["indicador_id"] == "SP.POP.TOTL"]
        
        if not datos_periodo:
            return None
        
        return min(datos_periodo, key=lambda x: x["valor"])["valor"]
    
    def calcular_promedio_poblacion(self, pais, año_inicio, año_fin):
        
        datos_periodo = [dato for dato in self.poblacion 
                        if dato["pais"] == pais and 
                           año_inicio <= dato["ano"] <= año_fin and
                           dato["indicador_id"] == "SP.POP.TOTL"]
        
        if not datos_periodo:
            return None
        
        return round(sum(dato["valor"] for dato in datos_periodo) / len(datos_periodo), 2)
    
    def contar_años_datos_disponibles(self, pais):
        
        años = set(dato["ano"] for dato in self.poblacion 
                  if dato["pais"] == pais and dato["indicador_id"] == "SP.POP.TOTL")
        
        return len(años)
    
    def paises_datos_completos(self, año_inicio, año_fin):
        
        paises_completos = []
        años_requeridos = set(range(año_inicio, año_fin + 1))
        
        for pais in self.paises:
            nombre_pais = pais["nombre"]
            años_disponibles = set(dato["ano"] for dato in self.poblacion 
                                  if dato["pais"] == nombre_pais and 
                                     dato["indicador_id"] == "SP.POP.TOTL")
            
            if años_requeridos.issubset(años_disponibles):
                paises_completos.append(nombre_pais)
        
        return paises_completos
    
    def años_crecimiento_mayor(self, pais, umbral):
        
        
        datos_pais = [dato for dato in self.poblacion 
                     if dato["pais"] == pais and dato["indicador_id"] == "SP.POP.TOTL"]
        
        datos_ordenados = sorted(datos_pais, key=lambda x: x["ano"])
        
        años_crecimiento = []
        for i in range(1, len(datos_ordenados)):
            año_actual = datos_ordenados[i]["ano"]
            pob_actual = datos_ordenados[i]["valor"]
            pob_anterior = datos_ordenados[i-1]["valor"]
            
            crecimiento = pob_actual - pob_anterior
            
            if crecimiento > umbral:
                años_crecimiento.append(año_actual)
        
        return años_crecimiento
    
    def obtener_poblacion_por_decada(self, pais, decada_inicio):
        
        
        decada_inicio = (decada_inicio // 10) * 10
        
        if not self.poblacion:
            return []
        
        año_máximo = max(dato["ano"] for dato in self.poblacion)
        
        resultados = []
        for década in range(decada_inicio, año_máximo + 10, 10): 
            def obtener_poblacion_por_decada(self, pais, decada_inicio):decada_inicio = (decada_inicio // 10) * 10
        
        if not self.poblacion:
            return []
        
        año_máximo = max(dato["ano"] for dato in self.poblacion)
        
        resultados = []
        for década in range(decada_inicio, año_máximo + 10, 10):
            
            datos_década = [dato for dato in self.poblacion 
                          if dato["pais"] == pais and
                             década <= dato["ano"] < década + 10 and
                             dato["indicador_id"] == "SP.POP.TOTL"]
            
            if datos_década:
                
                datos_ordenados = sorted(datos_década, key=lambda x: abs(x["ano"] - década))
                dato_representativo = datos_ordenados[0]
                
                resultados.append({
                    "decada": f"{década}s",
                    "año": dato_representativo["ano"],
                    "poblacion": dato_representativo["valor"]
                })
        
        return resultados
    
    def años_sin_datos(self, pais, año_inicio, año_fin):
        
        años_disponibles = set(dato["ano"] for dato in self.poblacion 
                              if dato["pais"] == pais and 
                                 dato["indicador_id"] == "SP.POP.TOTL")
        
        return [año for año in range(año_inicio, año_fin + 1) if año not in años_disponibles]
    
    def obtener_año_poblacion_maxima(self, pais):
        
        datos_pais = [dato for dato in self.poblacion 
                     if dato["pais"] == pais and dato["indicador_id"] == "SP.POP.TOTL"]
        
        if not datos_pais:
            return None
        
        return max(datos_pais, key=lambda x: x["valor"])["ano"]
    
    def años_datos_multiples_paises(self, umbral_paises):
        
        conteo_paises_por_año = {}
        
        for dato in self.poblacion:
            if dato["indicador_id"] == "SP.POP.TOTL":
                año = dato["ano"]
                pais = dato["pais"]
                
                if año not in conteo_paises_por_año:
                    conteo_paises_por_año[año] = set()
                
                conteo_paises_por_año[año].add(pais)
        
        return [año for año, paises in conteo_paises_por_año.items() 
               if len(paises) > umbral_paises]

def generar_reportes(sistema):
    
    while True:
        print("\n=== MÓDULO DE REPORTES ===")
        print("A. Datos de población 2000-2023")
        print("B. Listar países con códigos ISO")
        print("C. Datos de población 'SP.POP.TOTL'")
        print("D. Datos de población de los últimos 10 años")
        print("E. Total de población en 2022")
        print("F. Población total antes de 2000")
        print("G. Población total después de 2010")
        print("H. Porcentaje de crecimiento 2010-2020")
        print("I. Población en 2023")
        print("J. Año con población más baja")
        print("K. Número de registros por año")
        print("L. Países con crecimiento > 2% anual")
        print("M. Años con población > 1,000 millones")
        print("N. Población total en 2000")
        print("O. Población mínima en últimos 20 años")
        print("P. Promedio de población 1980-2020")
        print("Q. Años con datos de población")
        print("R. Países con datos 2000-2023")
        print("S. Población total en 2019")
        print("T. Años con crecimiento > 1 millón")
        print("U. Población por décadas desde 1960")
        print("V. Población total en 2023")
        print("W. Años sin datos de población")
        print("X. Año con población más alta")
        print("Y. Años con datos de más de 50 países")
        print("Z. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción (A-Z): ").upper()
        
        
        if opcion == 'A':
            print("\n=== DATOS DE POBLACIÓN 2000-2023 ===")
            for pais in sistema.listar_paises():
                datos = sistema.obtener_datos_poblacion_pais(pais['nombre'], 2000, 2023)
                print(f"\n{pais['nombre']}:")
                for dato in datos:
                    print(f"  Año: {dato['ano']}, Población: {dato['valor']:,} {dato['unidad']}")
        
        
        elif opcion == 'B':
            print("\n=== PAÍSES CON CÓDIGOS ISO ===")
            for pais in sistema.listar_paises():
                print(f"{pais['nombre']}: ISO2 {pais['codigo_iso']}, ISO3 {pais['codigo_iso3']}")
        
        
        elif opcion == 'C':
            print("\n=== DATOS SP.POP.TOTL ===")
            datos = sistema.obtener_datos_por_indicador("SP.POP.TOTL")
            for dato in datos:
                print(f"{dato['pais']} ({dato['ano']}): {dato['valor']:,} {dato['unidad']}")
        
        
        elif opcion == 'D':
            print("\n=== DATOS ÚLTIMOS 10 AÑOS ===")
            datos = sistema.obtener_datos_ultimos_años(10)
            for dato in datos:
                print(f"{dato['pais']} ({dato['ano']}): {dato['valor']:,} {dato['unidad']}")
        
        
        elif opcion == 'E':
            print("\n=== POBLACIÓN TOTAL 2022 ===")
            total = sistema.obtener_poblacion_total_año(2022)
            print(f"Población total en 2022: {total:,} personas")
        
        
        elif opcion == 'F':
            print("\n=== POBLACIÓN TOTAL ANTES DE 2000 ===")
            datos = sistema.obtener_poblacion_antes_año(2000)
            for dato in datos:
                print(f"{dato['pais']} ({dato['ano']}): {dato['valor']:,} {dato['unidad']}")
        
        
        elif opcion == 'G':
            print("\n=== POBLACIÓN TOTAL DESPUÉS DE 2010 ===")
            datos = sistema.obtener_poblacion_despues_año(2010)
            for dato in datos:
                print(f"{dato['pais']} ({dato['ano']}): {dato['valor']:,} {dato['unidad']}")
        
        
        elif opcion == 'H':
            print("\n=== PORCENTAJE DE CRECIMIENTO 2010-2020 ===")
            for pais in sistema.listar_paises():
                crecimiento = sistema.calcular_porcentaje_crecimiento(pais['nombre'], 2010, 2020)
                if crecimiento is not None:
                    print(f"{pais['nombre']}: {crecimiento}%")
        
        
        elif opcion == 'I':
            print("\n=== POBLACIÓN EN 2023 ===")
            for pais in sistema.listar_paises():
                poblacion = sistema.obtener_poblacion_pais_año(pais['nombre'], 2023)
                if poblacion is not None:
                    print(f"{pais['nombre']}: {poblacion:,} personas")
        
        
        elif opcion == 'J':
            print("\n=== AÑO CON POBLACIÓN MÁS BAJA ===")
            for pais in sistema.listar_paises():
                año = sistema.obtener_año_poblacion_minima(pais['nombre'])
                if año is not None:
                    poblacion = sistema.obtener_poblacion_pais_año(pais['nombre'], año)
                    print(f"{pais['nombre']}: Año {año}, Población {poblacion:,} personas")
        
        
        elif opcion == 'K':
            print("\n=== NÚMERO DE REGISTROS POR AÑO ===")
            registros = sistema.contar_registros_por_año()
            for año, num_registros in sorted(registros.items()):
                print(f"Año {año}: {num_registros} registros")
        
        
        elif opcion == 'L':
            print("\n=== PAÍSES CON CRECIMIENTO > 2% ANUAL ===")
            paises = sistema.paises_crecimiento_mayor(2, 5)
            for pais in paises:
                print(f"{pais['pais']}: {pais['crecimiento_promedio']}%")
        
        
        elif opcion == 'M':
            print("\n=== AÑOS CON POBLACIÓN > 1,000 MILLONES ===")
            for pais in sistema.listar_paises():
                años = sistema.años_poblacion_mayor(pais['nombre'], 1_000_000_000)
                if años:
                    print(f"{pais['nombre']}: {años}")
        
        
        elif opcion == 'N':
            print("\n=== POBLACIÓN TOTAL EN 2000 ===")
            total = sistema.obtener_poblacion_total_año(2000)
            print(f"Población total en 2000: {total:,} personas")
        
        
        elif opcion == 'O':
            print("\n=== POBLACIÓN MÍNIMA EN ÚLTIMOS 20 AÑOS ===")
            for pais in sistema.listar_paises():
                poblacion_min = sistema.obtener_poblacion_minima_periodo(pais['nombre'], 20)
                if poblacion_min is not None:
                    print(f"{pais['nombre']}: {poblacion_min:,} personas")
        
        
        elif opcion == 'P':
            print("\n=== PROMEDIO DE POBLACIÓN 1980-2020 ===")
            for pais in sistema.listar_paises():
                promedio = sistema.calcular_promedio_poblacion(pais['nombre'], 1980, 2020)
                if promedio is not None:
                    print(f"{pais['nombre']}: {promedio:,} personas")
        
        
        elif opcion == 'Q':
            print("\n=== AÑOS CON DATOS DE POBLACIÓN ===")
            for pais in sistema.listar_paises():
                años = sistema.contar_años_datos_disponibles(pais['nombre'])
                print(f"{pais['nombre']}: {años} años")
        
        
        elif opcion == 'R':
            print("\n=== PAÍSES CON DATOS 2000-2023 ===")
            paises = sistema.paises_datos_completos(2000, 2023)
            print("Países con datos completos:", paises)
        
       
        elif opcion == 'S':
            print("\n=== POBLACIÓN TOTAL EN 2019 ===")
            total = sistema.obtener_poblacion_total_año(2019)
            print(f"Población total en 2019: {total:,} personas")
        
        
        elif opcion == 'T':
            print("\n=== AÑOS CON CRECIMIENTO > 1 MILLÓN ===")
            for pais in sistema.listar_paises():
                años = sistema.años_crecimiento_mayor(pais['nombre'], 1_000_000)
                if años:
                    print(f"{pais['nombre']}: {años}")
        
        
        elif opcion == 'U':
            print("\n=== POBLACIÓN POR DÉCADAS DESDE 1960 ===")
            for pais in sistema.listar_paises():
                poblacion_decadas = sistema.obtener_poblacion_por_decada(pais['nombre'], 1960)
                print(f"\n{pais['nombre']}:")
                for registro in poblacion_decadas:
                    print(f"  {registro['decada']}: {registro['poblacion']:,} personas (año {registro['año']})")
        
        
        elif opcion == 'V':
            print("\n=== POBLACIÓN TOTAL EN 2023 ===")
            total = sistema.obtener_poblacion_total_año(2023)
            print(f"Población total en 2023: {total:,} personas")
        
        
        elif opcion == 'W':
            print("\n=== AÑOS SIN DATOS DE POBLACIÓN ===")
            for pais in sistema.listar_paises():
                años = sistema.años_sin_datos(pais['nombre'], 2000, 2023)
                if años:
                    print(f"{pais['nombre']}: {años}")
        
        
        elif opcion == 'X':
            print("\n=== AÑO CON POBLACIÓN MÁS ALTA ===")
            for pais in sistema.listar_paises():
                año = sistema.obtener_año_poblacion_maxima(pais['nombre'])
                if año is not None:
                    poblacion = sistema.obtener_poblacion_pais_año(pais['nombre'], año)
                    print(f"{pais['nombre']}: Año {año}, Población {poblacion:,} personas")
        
        
        elif opcion == 'Y':
            print("\n=== AÑOS CON DATOS DE MÁS DE 50 PAÍSES ===")
            años = sistema.años_datos_multiples_paises(50)
            print("Años:", años)


        
        