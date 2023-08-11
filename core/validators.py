# import psycopg2
#
# conn = psycopg2.connect(
#     database="estore", user='postgres', password='VA0885281774', host='127.0.0.1', port='5432'
# )
# conn.autocommit = True
# cursor = conn.cursor()
# cursor.execute('''SELECT bulstat from core_firm''')
# result = cursor.fetchall()
# data_bulstat = []
# for i in range(len(result)):
#     data_bulstat.append(result[i][0])
# conn.commit()
# conn.close()
#
# conn = psycopg2.connect(
#     database="estore", user='postgres', password='VA0885281774', host='127.0.0.1', port='5432'
# )
# conn.autocommit = True
# cursor = conn.cursor()
# cursor.execute('''SELECT "vat_number" from core_firm''')
# result = cursor.fetchall()
# data_vat = []
# for i in range(len(result)):
#     data_vat.append(result[i][0])
# conn.commit()
# conn.close()
#
# conn = psycopg2.connect(
#     database="estore", user='postgres', password='VA0885281774', host='127.0.0.1', port='5432'
# )
# conn.autocommit = True
# cursor = conn.cursor()
# cursor.execute('''SELECT "VAT_number" from core_ownerfirm''')
# result = cursor.fetchall()
# data_vat_owner = []
# for i in range(len(result)):
#     data_vat_owner.append(result[i][0])
# conn.commit()
# conn.close()
#
# conn = psycopg2.connect(
#     database="estore", user='postgres', password='VA0885281774', host='127.0.0.1', port='5432'
# )
# conn.autocommit = True
# cursor = conn.cursor()
# cursor.execute('''SELECT "bulstat" from core_ownerfirm''')
# result = cursor.fetchall()
# data_owner = []
# for i in range(len(result)):
#     data_owner.append(result[i][0])
# conn.commit()
# conn.close()
#
#
# def check_vat_number(value):
#     if not value[0:2] == "BG":
#         raise ValidationError("Номерът по ЗДДС трябва да започва с 'BG'")
#     for i in value[2:10]:
#         if not i.isdigit():
#             raise ValidationError("Номерът по ЗДДС трябва да съдържа само цифри и 'BG'")
#
#
# def check_unique_vat_number_firms(value):
#     if value:
#         for i in data_vat:
#             if not i is None:
#                 if i == value:
#                     raise ValidationError(
#                         "Номерът по ЗДДС на фирмата трябва да бъде единствен. Вече съществува фирма с такъв номер")
#
#
# def check_unique_vat_number_owner_firms(value):
#     if value:
#         for i in data_vat_owner:
#             if not i is None:
#                 if i == value:
#                     raise ValidationError(
#                         "Номерът по ЗДДС на фирмата трябва да бъде единствен. Вече съществува фирма с такъв номер")
#
#
# def check_unique(value):
#     if value:
#         for i in data_bulstat:
#             if not i is None:
#                 if i[0] == value:
#                     raise ValidationError("ЕИК на фирмата трябва да бъде единствен. Вече съществува фирма с такъв ЕИК")
#
#
# def check_unique_bulstat_owner_firms(value):
#     if value:
#         for i in data_owner:
#             if not i is None:
#                 if i == value:
#                     raise ValidationError("ЕИК на фирмата трябва да бъде единствен. Вече съществува фирма с такъв ЕИК")
#
#
# def check_bulstat(value):
#     for i in value:
#         if not i.isdigit():
#             raise ValidationError("ЕИК трябва да съдържа само цифри")
