import csv

with open('uscities.csv','r') as csvinput:
    with open('uscities_updated.csv', 'w') as csvoutput:
        writer = csv.writer(csvoutput, lineterminator='\n')
        reader = csv.reader(csvinput)

        all = []
        row = next(reader)
        row.append('city_state')
        all.append(row)

        for row in reader:
            row.append(row[0] + ", " + row[2])
            all.append(row)

        writer.writerows(all)