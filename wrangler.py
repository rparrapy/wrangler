
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import utm
import click
import csv
import datetime

@click.command()
@click.option('--input', prompt='Ingrese el nombre del archivo de entrada', help='Ruta al archivo csv de entrada.')
@click.option('--sector', default=0, help='Indice de la columna del sector.')
@click.option('--y', default=1, help='Nombre de la columna dey.')
@click.option('--x', default=2, help='Nombre de la columna dey.')
@click.option('--output', default='output.json', help='Ruta al archivo csv de salida.')
@click.option('--verbose', is_flag=False)
def convert_csv(input, sector, y, x, output, verbose):

     # Read in raw data from csv
    rawData = csv.reader(open(input, 'rbU'), delimiter=';', dialect=csv.excel_tab)
    #resultWriter = csv.writer(open(output, 'wb'), delimiter=';', dialect='excel')
    result = []
    header = []
    
    utm_cols = [sector, y, x]

    iter = 0
    cont = 0
    for row in rawData:
        iter += 1
        content = [row[i] for i in range(len(row)) if i not in utm_cols]
        if iter >= 2:
            elem_sector = row[sector].replace(" ", "")

            try:
                elem_letter = elem_sector[-1]
                elem_number = int(elem_sector[:-1])
                elem_y = int(row[y])
                elem_x = int(row[x])
            except (ValueError, IndexError), e:
                if verbose:
                    print "Sin coordenadas: %s" % (row, )
                continue

            try:
                lat_long = utm.to_latlon(elem_x, elem_y, elem_number, elem_letter)
                #print [str(c) for c in lat_long]
            except utm.error.OutOfRangeError, e:
                print "Coordenadas invalidas: %s %s %s" % (elem_sector, elem_y, elem_x)
                continue

            content = [str(c) for c in lat_long] + content
            result.append(content)

        else:
            content = ['latitude', 'longitude'] + content
            header += content
        
        #print 'about to write row: %s' % content
        #resultWriter.writerow(content)
        cont += 1

    print 'Se convirtieron %s filas' % cont
    csv_to_geojson(result, header, output)
    # Hasta aca conversion a CSV


def csv_to_geojson(rows, header, out_file):
    # the template. where data from the csv will be formatted to geojson
    template = \
        ''' \
        {   
            "type" : "Feature",
            "geometry" : {
                "type" : "Point",
                "coordinates" : [%s, %s]},
                "properties" : {
                    %s
                }
        },
        '''
     
    # the head of the geojson file
    output = \
        ''' \
    { "type" : "FeatureCollection",
      "features" : [
        '''


    for i, row in enumerate(rows):
        latitud = row[0]
        longitud = row[1]
        properties = ""
        for j in range(2, len(row)):
            if header[j] and row[j]:
                value = row[j].replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t").decode("utf8")
                try:
                    value = int(value)
                except ValueError:
                    pass

                if isinstance(value, basestring):
                    value = '"' + value + '"'
                properties += '\t\t\t\t\t"%s":%s,\n' % (header[j].decode("utf8"), value)
        properties = properties[5:-2]
        output += template % (longitud, latitud, properties)



    # the tail of the geojson file
    output = output[:-10]
    output += \
        ''' \
        ]
    }
        '''

    outFileHandle = open(out_file, "w")
    outFileHandle.write(output.encode("utf8"))
    outFileHandle.close()


if __name__ == '__main__':
    convert_csv()