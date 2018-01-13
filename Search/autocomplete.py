

ingred_s = open('Search/ingre_sort.txt')
name_s = open('Search/name_sort.txt')

ingredients = [l.split()[0].decode('utf-8') for l in ingred_s.readlines()]
names = [l.split()[0] for l in name_s.readlines()]