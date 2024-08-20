import YeniTestSonucu
import cevap


def degerlendir(ogrenci_path, cevap_path):

    cevaplar = cevap.cevapoku(cevap_path)
    ogrenci = YeniTestSonucu.oku(ogrenci_path)

    cvp_mat = cevaplar.get("matematik")
    cvp_tr = cevaplar.get("türkçe")
    cvp_sos = cevaplar.get("sosyal")
    cvp_fen = cevaplar.get("fen")

    ogr_mat = ogrenci.get("matematik")
    ogr_tr = ogrenci.get("türkçe")
    ogr_sos = ogrenci.get("sosyal")
    ogr_fen = ogrenci.get("fen")

    dogrular = 0
    yanlislar = 0

    for i in range(1, 41):
        if cvp_mat[i] == ogr_mat[i]:
            dogrular += 1
        else:
            yanlislar += 1
    
    for i in range(1, 41):
        if cvp_tr[i] == ogr_tr[i]:
            dogrular += 1
        else:
            yanlislar += 1
    
    for i in range(1, 41):
        if cvp_sos[i] == ogr_sos[i]:
            dogrular += 1
        else:
            yanlislar += 1

    for i in range(1, 41):
        if cvp_fen[i] == ogr_fen[i]:
            dogrular += 1
        else:
            yanlislar += 1

    ogr_no = ogrenci.get("ogr_no")
    kurum_no = ogrenci.get("kurum_kodu")
    sinav_no = ogrenci.get("sınav_kodu")


    return dogrular, yanlislar,ogr_no, kurum_no, sinav_no
