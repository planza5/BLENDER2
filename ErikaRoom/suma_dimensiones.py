import bpy

def calcular_distribucion():
    # Configuracion de tableros (5 tableros de 244 x 39.5 x 1.6 cm)
    LARGO_TABLERO_CM = 244
    ANCHO_TABLERO_CM = 39.5
    GROSOR_TABLERO_CM = 1.6
    NUM_TABLEROS = 5

    piezas = []

    print("LISTADO DE PIEZAS (dimensiones en cm):")
    print("-" * 70)

    for obj in bpy.context.scene.objects:
        if obj.type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME'}:
            dims_cm = sorted(list(obj.dimensions))
            grosor = dims_cm[0]
            ancho = dims_cm[1]
            largo = dims_cm[2]

            # Verificar si la pieza cabe en un tablero
            cabe_largo = largo <= LARGO_TABLERO_CM
            cabe_ancho = ancho <= ANCHO_TABLERO_CM

            if cabe_largo and cabe_ancho:
                estado = "OK"
            elif not cabe_largo:
                estado = "MUY LARGA"
            else:
                estado = "MUY ANCHA"

            piezas.append({
                'nombre': obj.name,
                'largo': largo,
                'ancho': ancho,
                'grosor': grosor,
                'estado': estado
            })
            print(f"{obj.name}:")
            print(f"    {grosor:.2f} x {ancho:.2f} x {largo:.2f} cm [{estado}]")

    # Verificar piezas con problemas
    piezas_problemas = [p for p in piezas if p['estado'] != "OK"]
    if piezas_problemas:
        print(f"\n{'='*70}")
        print("RESULTADO: NO FACTIBLE")
        print(f"{'='*70}")
        for p in piezas_problemas:
            print(f"  - {p['nombre']}: {p['estado']} ({p['largo']:.2f} x {p['ancho']:.2f} cm)")
        return

    # Algoritmo First Fit Decreasing para distribuir piezas
    piezas_ordenadas = sorted(piezas, key=lambda x: x['largo'], reverse=True)

    tableros = []  # Lista de tableros, cada uno con sus piezas y espacio usado

    for pieza in piezas_ordenadas:
        colocada = False
        for tablero in tableros:
            if tablero['espacio_restante'] >= pieza['largo']:
                tablero['piezas'].append(pieza)
                tablero['espacio_restante'] -= pieza['largo']
                colocada = True
                break

        if not colocada:
            # Crear nuevo tablero
            tableros.append({
                'piezas': [pieza],
                'espacio_restante': LARGO_TABLERO_CM - pieza['largo']
            })

    tableros_necesarios = len(tableros)
    suma_largos = sum(p['largo'] for p in piezas)

    # Resultado
    print(f"\n{'='*70}")
    print("RESUMEN")
    print(f"{'='*70}")
    print(f"Piezas totales: {len(piezas)}")
    print(f"Suma de largos: {suma_largos:.2f} cm")
    print(f"Tableros disponibles: {NUM_TABLEROS} de {LARGO_TABLERO_CM} x {ANCHO_TABLERO_CM} cm")
    print(f"Tableros necesarios: {tableros_necesarios}")

    print(f"\n{'='*70}")
    if tableros_necesarios <= NUM_TABLEROS:
        sobrantes = NUM_TABLEROS - tableros_necesarios
        print(f"RESULTADO: FACTIBLE")
        print(f"Caben en {tableros_necesarios} tableros (te sobran {sobrantes})")

        # Mostrar distribucion de cortes
        print(f"\n{'='*70}")
        print("DISTRIBUCION DE CORTES:")
        print(f"{'='*70}")
        for i, tablero in enumerate(tableros, 1):
            usado = LARGO_TABLERO_CM - tablero['espacio_restante']
            print(f"\nTABLERO {i} de {LARGO_TABLERO_CM} cm ({usado:.2f} cm usados, {tablero['espacio_restante']:.2f} cm sobrante):")
            for p in tablero['piezas']:
                print(f"    - {p['nombre']}: {p['largo']:.2f} cm")
    else:
        faltan = tableros_necesarios - NUM_TABLEROS
        print(f"RESULTADO: NO FACTIBLE con {NUM_TABLEROS} tableros de {LARGO_TABLERO_CM} cm")
        print(f"Necesitas {tableros_necesarios} tableros en total")

        # Calcular lo que queda para los tableros extra
        piezas_en_extras = []
        for t in tableros[NUM_TABLEROS:]:
            piezas_en_extras.extend(t['piezas'])

        largo_extra_necesario = sum(p['largo'] for p in piezas_en_extras)
        pieza_mas_larga_extra = max(p['largo'] for p in piezas_en_extras) if piezas_en_extras else 0

        print(f"\nSOLUCION:")
        print(f"  Comprar {faltan} tablero(s) adicional(es)")
        print(f"  Largo minimo necesario: {pieza_mas_larga_extra:.1f} cm")
        print(f"  (para cubrir {largo_extra_necesario:.1f} cm de piezas)")

        # Mostrar distribucion de cortes
        print(f"\n{'='*70}")
        print("DISTRIBUCION DE CORTES:")
        print(f"{'='*70}")

        for i, tablero in enumerate(tableros[:NUM_TABLEROS], 1):
            usado = LARGO_TABLERO_CM - tablero['espacio_restante']
            print(f"\nTABLERO {i} de {LARGO_TABLERO_CM} cm ({usado:.2f} cm usados, {tablero['espacio_restante']:.2f} cm sobrante):")
            for p in tablero['piezas']:
                print(f"    - {p['nombre']}: {p['largo']:.2f} cm")

        # Tableros adicionales
        for i, tablero in enumerate(tableros[NUM_TABLEROS:], NUM_TABLEROS + 1):
            usado = LARGO_TABLERO_CM - tablero['espacio_restante']
            print(f"\nTABLERO EXTRA {i} (minimo {pieza_mas_larga_extra:.1f} cm):")
            for p in tablero['piezas']:
                print(f"    - {p['nombre']}: {p['largo']:.2f} cm")

    print(f"\n{'='*70}")

# Ejecutar
calcular_distribucion()
