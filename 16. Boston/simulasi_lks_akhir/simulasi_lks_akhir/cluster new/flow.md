1. Pengecekan data awal (info, describe, shape, head, na, duplicate)
2. Pengecekkan Outlier (Rata2 outlier kuanggap data asli yang sangat bervariasi)
3. Ngebuat Medv jadi class make lambda
4. ngeliat distribusi aneh make histplot
5. Nentuin dummy material di dummy subject terus bikin for loop buat ngedummy kolom2nya
6. Dummy yang kutentuin: CRIM (kriminalitas tinggi gaada yg mau tinggal), NOX (Polusi tinggi gaada yg mau tinggal), RM (Ruangan banyak = big hous = big money), B (Rasis?), TAX(Pajak yg tinggi bikin org gamau beli rumah), LSTAT(Tingkat orang yg kurang ngasih tau banyak tentang daerah mereka tinggal, yang biasanya tidak dikelilingi rumah glamor), sama ZN (kalo ada lahan luas di perumahan, mereka akan memikirkan untuk masuk di perumahan tsb)
7. Pengecekan korelasi dengan MEDV
8. Pairplot dan Heatmap
9. Ngedrop Kolom chas, rad
10. Oversampling
11. Stratified Split
12. SMOTE
13. Scaling
14. Model SVM dan RFC
15. pengecekan akurasi, CM, dan Classification Report (Meskipun 98, aku yakin random forest overfitting)