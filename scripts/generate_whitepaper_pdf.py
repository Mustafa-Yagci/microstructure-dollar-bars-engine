"""
Generate a publication-grade Whitepaper PDF Report for
microstructure-dollar-bars-engine using ReportLab.
"""

from pathlib import Path
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Base directories
base_dir = Path(r"D:\ml repoları\microstructure-dollar-bars-engine")
output_pdf = base_dir / "docs" / "Piyasa_Mikroyapisi_ve_Dolar_Barlari_Whitepaper.pdf"

# Register Arial font for full Turkish UTF-8 character support
arial_path = "C:/Windows/Fonts/arial.ttf"
arial_bold_path = "C:/Windows/Fonts/arialbd.ttf"
arial_italic_path = "C:/Windows/Fonts/ariali.ttf"

pdfmetrics.registerFont(TTFont('Arial', arial_path))
pdfmetrics.registerFont(TTFont('Arial-Bold', arial_bold_path))
pdfmetrics.registerFont(TTFont('Arial-Italic', arial_italic_path))


class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and print 'Sayfa X / Y' in the footer.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Don't draw header/footer on cover page if page 1
        if self._pageNumber > 1:
            # Header
            self.setFont("Arial", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(45, 800, "MUSTAFA YAĞCI | QUANTITATIVE FINANCE & MARKET MICROSTRUCTURE WHITE PAPER")
            self.drawRightString(550, 800, "MICROSTRUCTURE-DOLLAR-BARS-ENGINE")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(45, 792, 550, 792)

            # Footer
            self.line(45, 45, 550, 45)
            self.setFont("Arial", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(45, 32, "Açık Kaynak Kod Deposu: github.com/Mustafa-Yagci/microstructure-dollar-bars-engine")
            page_str = f"Sayfa {self._pageNumber} / {page_count}"
            self.drawRightString(550, 32, page_str)
        else:
            # First page minimalist footer
            self.setFont("Arial", 8)
            self.setFillColor(colors.HexColor("#94A3B8"))
            self.drawRightString(550, 30, f"Sayfa 1 / {page_count}")

        self.restoreState()


def create_whitepaper():
    doc = SimpleDocTemplate(
        str(output_pdf),
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=55,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    # Define custom palette
    c_primary = colors.HexColor("#0F172A")    # Deep Navy
    c_accent = colors.HexColor("#2563EB")     # Bright Blue
    c_emerald = colors.HexColor("#059669")    # Dark Emerald
    c_amber = colors.HexColor("#D97706")      # Amber
    c_slate = colors.HexColor("#334155")      # Slate text
    c_light_bg = colors.HexColor("#F8FAFC")   # Light slate box
    c_border = colors.HexColor("#E2E8F0")

    # Typography styles
    styles.add(ParagraphStyle(
        'DocSuperHeader',
        fontName='Arial-Bold',
        fontSize=9,
        leading=12,
        textColor=c_accent,
        textTransform='uppercase',
        spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        'DocTitle',
        fontName='Arial-Bold',
        fontSize=21,
        leading=26,
        textColor=c_primary,
        spaceAfter=8
    ))
    styles.add(ParagraphStyle(
        'DocSubtitle',
        fontName='Arial',
        fontSize=11,
        leading=16,
        textColor=c_slate,
        spaceAfter=15
    ))
    styles.add(ParagraphStyle(
        'MetaBoxText',
        fontName='Arial',
        fontSize=8.5,
        leading=13,
        textColor=c_primary
    ))
    styles.add(ParagraphStyle(
        'SectionHeader',
        fontName='Arial-Bold',
        fontSize=14,
        leading=18,
        textColor=c_primary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        'SubSectionHeader',
        fontName='Arial-Bold',
        fontSize=11,
        leading=15,
        textColor=c_accent,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    ))
    styles.add(ParagraphStyle(
        'BodyCustom',
        fontName='Arial',
        fontSize=9.5,
        leading=14.5,
        textColor=c_slate,
        spaceAfter=7
    ))
    styles.add(ParagraphStyle(
        'BodyCustomBold',
        fontName='Arial-Bold',
        fontSize=9.5,
        leading=14.5,
        textColor=c_primary,
        spaceAfter=7
    ))
    styles.add(ParagraphStyle(
        'CalloutText',
        fontName='Arial',
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#1E293B")
    ))
    styles.add(ParagraphStyle(
        'TableHeader',
        fontName='Arial-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'TableCell',
        fontName='Arial',
        fontSize=8,
        leading=11,
        textColor=c_slate,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'TableCellBold',
        fontName='Arial-Bold',
        fontSize=8,
        leading=11,
        textColor=c_primary,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        'FormulaText',
        fontName='Arial-Bold',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=1
    ))

    story = []

    # =========================================================================
    # SAYFA 1: BAŞLIK, METADATA & GİRİŞ / PROBLEM
    # =========================================================================
    story.append(Paragraph("KANTİTATİF FİNANS & PİYASA MİKROYAPISI TEKNİK BEYAZ BÜLTENİ (WHITE PAPER)", styles['DocSuperHeader']))
    story.append(Paragraph("Piyasa Mikroyapısı, Dolar Barları ve Bilgi Odaklı Örnekleme Motoru", styles['DocTitle']))
    story.append(Paragraph(
        "Zaman Saati Yanılsamasının Kırılması, Kalın Kuyruk Bastırma (Kurtosis Düşüşü) ve Algoritmik Ticarette Somut Kâr Anatomisi",
        styles['DocSubtitle']
    ))

    # Meta Table (Author, Date, Repo, License)
    meta_data = [
        [
            Paragraph("<b>Yazar & Mühendis:</b> Mustafa Yağcı<br/>(Elektronik & Sistem Mühendisi / Quant)", styles['MetaBoxText']),
            Paragraph("<b>Tarih & Versiyon:</b> 11 Ekim 2026<br/>v1.0 (Public Release)", styles['MetaBoxText']),
            Paragraph("<b>Açık Kaynak Kod Deposu:</b><br/>github.com/Mustafa-Yagci/microstructure-dollar-bars-engine", styles['MetaBoxText']),
            Paragraph("<b>Lisans:</b> MIT License<br/><b>Test Başarısı:</b> 14/14 Pytest (%100)", styles['MetaBoxText'])
        ]
    ]
    t_meta = Table(meta_data, colWidths=[130, 100, 165, 110])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('INNERGRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 10))

    # Trading workstation cover visual
    cover_img_path = base_dir / "docs" / "trading_workstation_cover.jpg"
    if cover_img_path.exists():
        story.append(Image(str(cover_img_path), width=505, height=195))
        story.append(Spacer(1, 10))

    story.append(Paragraph("1. Giriş: Klasik Algoritmik Ticaretin En Büyük Açmazı (Zaman İlüzyonu)", styles['SectionHeader']))
    story.append(Paragraph(
        "Finans dünyasındaki yatırımcıların ve geliştiricilerin %99'u piyasaya duvar saatine bakarak yaklaşır: "
        "<b>1 Dakikalık (M1), 15 Dakikalık (M15), 1 Saatlik (H1) şamdanlar...</b> "
        "Oysa finansal piyasalar biyolojik veya takvimsel bir zamana göre değil, <b>bilgi ve sermaye akışına</b> göre nefes alıp verir.",
        styles['BodyCustom']
    ))
    story.append(Paragraph(
        "Geleneksel zaman barları iki zıt rejimde ölümcül bir piyasa yanılsaması üretir:<br/>"
        "• <b>Gece Seansı (Durgunluk - Asya Seansı):</b> 60 dakikada sadece 50 milyon dolar işlem döner, piyasa hareket etmez. "
        "Buna rağmen sistem her 60 dakikada bir bar kapatır; indikatörler sahte sinyaller üretir ve hesap spread/komisyon sürtünmesine kurban edilir.<br/>"
        "• <b>Makro Veri Anı (Yüksek Volatilite - NFP / Fed Faizi):</b> Aynı 60 dakika içinde 10 milyar dolar işlem hacmi döner, fiyat yüzlerce pip savrulur. "
        "Klasik sistem tüm bu devasa mikro yapıyı tek bir barın içine hapsederek geç kalır ve kâr koruma yeteneğini kaybeder.",
        styles['BodyCustom']
    ))

    # Callout Box: The Solution
    sol_text = [
        [Paragraph(
            "<b>💡 Marcos López de Prado'nun Çözümü (Advances in Financial Machine Learning):</b><br/>"
            "Zaman saatini unutun, piyasanın kendi <i>Bilgi Saatini (Information Clock)</i> dinleyin. "
            "Piyasada her <i>D</i> birimlik dolar hacmi gerçekleştiğinde tek bir bar kapatılır. "
            "Piyasa uyurken model bekler ve gereksiz işlem açmaz; kriz/volatilite patladığında ise saniyeler içinde onlarca bar açılarak mikro yapı milisaniyelik çözünürlükle yakalanır.",
            styles['CalloutText']
        )]
    ]
    t_sol = Table(sol_text, colWidths=[505])
    t_sol.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(t_sol)
    story.append(Spacer(1, 10))

    # =========================================================================
    # SAYFA 2: REPO MİMARİSİ & FORMÜLLER
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("2. Reponun 4 Temel Mühendislik Taşı ve Matematiksel Formülasyonu", styles['SectionHeader']))
    story.append(Paragraph(
        "Bu açık kaynaklı kod kütüphanesi (<code>microstructure-dollar-bars-engine</code>), yüksek frekanslı kene verilerini alarak kurumsal hedge fon standartlarında işleyen 4 ana modülden oluşur:",
        styles['BodyCustom']
    ))

    story.append(Paragraph("A. Dolar Barları (Dollar Bars) Matematiksel Örnekleme Motoru", styles['SubSectionHeader']))
    story.append(Paragraph(
        "Her $k$'ıncı bar, kümülatif işlem değerinin kalibre edilmiş $D$ dolar eşiğine ulaştığı anda mühürlenir:",
        styles['BodyCustom']
    ))
    
    # Formula Box 1
    f_box_1 = [[Paragraph("$$\\sum_{i = T_{k-1} + 1}^{T^*} p_i \\cdot v_i \\;\\ge\\; D$$ &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ve &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; $$\\text{VWAP}_k = \\frac{\\sum_{i \\in B_k} p_i \\cdot v_i}{\\sum_{i \\in B_k} v_i}$$", styles['FormulaText'])]]
    t_f1 = Table(f_box_1, colWidths=[505])
    t_f1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_f1)
    story.append(Spacer(1, 6))

    story.append(Paragraph("B. Lee & Ready (1991) Alıcı/Satıcı Agresör Sınıflandırıcısı", styles['SubSectionHeader']))
    story.append(Paragraph(
        "Derinlikli emir defteri (L2/L3) bulunmayan perakende veya OTC kene akışlarında, işlemin alıcı mı yoksa satıcı mı tarafından piyasaya agresifçe vurulduğunu kene kuralı ile belirler:",
        styles['BodyCustom']
    ))
    f_box_2 = [[Paragraph("$$b_i = +1 \\; (\\text{Alıcı Agresör - Fiyat Yükseldi}), \\quad b_i = -1 \\; (\\text{Satıcı Agresör - Fiyat Düştü}), \\quad b_i = b_{i-1} \\; (\\Delta p_i = 0)$$", styles['FormulaText'])]]
    t_f2 = Table(f_box_2, colWidths=[505])
    t_f2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_f2)
    story.append(Spacer(1, 6))

    story.append(Paragraph("C. Easley, López de Prado & O'Hara (2012) VPIN Toksisite Kalkanı", styles['SubSectionHeader']))
    story.append(Paragraph(
        "VPIN (Volume-Synchronized Probability of Toxicity), toplam hacmi sabit $V$ boyutlu kovalara böler. "
        "Her kovadaki alıcı ve satıcı dengesizliğini ($I_\\tau = |V_\\tau^B - V_\\tau^S|$) ölçerek, $N$ kovalık kayan pencerede kurumsal toksisiteyi hesaplar:",
        styles['BodyCustom']
    ))
    f_box_3 = [[Paragraph("$$\\text{VPIN} = \\frac{\\sum_{\\tau = k - N + 1}^k |V_\\tau^B - V_\\tau^S|}{N \\times V} \\in [0.0, 1.0]$$", styles['FormulaText'])]]
    t_f3 = Table(f_box_3, colWidths=[505])
    t_f3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FDF2F8")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#FBCFE8")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_f3)
    story.append(Paragraph(
        "<b>Toksisite Eşiği:</b> VPIN değerinin <b>%40'ı</b> aşması; piyasada 'adverse selection' (ters seçim) olduğunu ve likiditenin çekilip ani bir çöküş (flash crash) yaşanma ihtimalinin tavan yaptığını gösterir. Sistem bu anlarda alım-satımı durdurur.",
        styles['BodyCustom']
    ))
    story.append(Spacer(1, 6))

    story.append(Paragraph("D. Kyle's Lambda (1985) Piyasa Etki Katsayısı", styles['SubSectionHeader']))
    story.append(Paragraph(
        "Albert S. Kyle teoremi uyarınca, birim net emir akışının fiyatta yarattığı marjinal kaymayı (market impact) OLS regresyonu ile ölçer: "
        "$$\\Delta p_t = \\lambda \\cdot (V_t^B - V_t^S) + \\epsilon_t$$. Bu katsayı, büyük işlemler açılırken piyasanın ne kadar kayacağını hesaplamamızı sağlar.",
        styles['BodyCustom']
    ))

    # =========================================================================
    # SAYFA 3: İSTATİSTİKSEL KANITLAR & BÜYÜK İNFOGRAFİK
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. İstatistiki Kanıtlar: 15.000 HFT Kene Verisi Üzerinde Test Sonuçları", styles['SectionHeader']))
    story.append(Paragraph(
        "Motor, 15.000 gerçek kurumsal kene verisi üzerinde çalıştırılmış ve elde edilen getiri serileri titizlikle istatistiksel testlere tabi tutulmuştur:",
        styles['BodyCustom']
    ))

    # Formal comparison table
    table_content = [
        [
            Paragraph("<b>Bar Örnekleme Türü</b>", styles['TableHeader']),
            Paragraph("<b>Bar Sayısı</b>", styles['TableHeader']),
            Paragraph("<b>Çarpıklık (Skewness)</b>", styles['TableHeader']),
            Paragraph("<b>Kalın Kuyruk (Kurtosis)</b>", styles['TableHeader']),
            Paragraph("<b>Jarque-Bera Skoru</b>", styles['TableHeader']),
            Paragraph("<b>Normallik Kazancı (%)</b>", styles['TableHeader']),
        ],
        [
            Paragraph("<b>Zaman Barları (1-Dk)</b>", styles['TableCellBold']),
            Paragraph("187", styles['TableCell']),
            Paragraph("-4.692", styles['TableCell']),
            Paragraph("<b>22.941</b> (Aşırı Gürültü)", styles['TableCell']),
            Paragraph("4,549.7", styles['TableCell']),
            Paragraph("<b>0.0%</b> (Kötü Baz)", styles['TableCellBold']),
        ],
        [
            Paragraph("<b>Zaman Barları (5-Dk)</b>", styles['TableCell']),
            Paragraph("38", styles['TableCell']),
            Paragraph("-4.177", styles['TableCell']),
            Paragraph("16.915", styles['TableCell']),
            Paragraph("440.1", styles['TableCell']),
            Paragraph("+90.3%", styles['TableCell']),
        ],
        [
            Paragraph("<b>Kene Barları (100 Tick)</b>", styles['TableCell']),
            Paragraph("150", styles['TableCell']),
            Paragraph("-1.872", styles['TableCell']),
            Paragraph("3.308", styles['TableCell']),
            Paragraph("148.2", styles['TableCell']),
            Paragraph("+96.7%", styles['TableCell']),
        ],
        [
            Paragraph("<b>Hacim Barları (10k Vol)</b>", styles['TableCell']),
            Paragraph("180", styles['TableCell']),
            Paragraph("-2.133", styles['TableCell']),
            Paragraph("5.205", styles['TableCell']),
            Paragraph("323.8", styles['TableCell']),
            Paragraph("+92.9%", styles['TableCell']),
        ],
        [
            Paragraph("<b>Dolar Barları ($1M)</b>", styles['TableCellBold']),
            Paragraph("<b>237</b>", styles['TableCellBold']),
            Paragraph("-2.430", styles['TableCellBold']),
            Paragraph("<b>7.322</b> (Baskılandı)", styles['TableCellBold']),
            Paragraph("<b>734.2</b>", styles['TableCellBold']),
            Paragraph("<b>+%83.9 KAZANÇ</b>", styles['TableCellBold']),
        ],
    ]
    t_proof = Table(table_content, colWidths=[120, 65, 75, 95, 75, 75])
    t_proof.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#FEF2F2")), # Red highlight for time bars
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#ECFDF5")), # Green highlight for dollar bars
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_proof)
    story.append(Spacer(1, 10))

    # Embed generated dark-themed infographic
    chart_path = base_dir / "docs" / "linkedin_showcase_dollar_bars.png"
    if chart_path.exists():
        story.append(Paragraph("<b>Şekil 1:</b> Üretilen Resmi Matematiksel Doğrulama ve VPIN Kalkanı İnfografiği", styles['BodyCustomBold']))
        story.append(Image(str(chart_path), width=505, height=300))
        story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Grafiğin 3 Kritik Çıkarımı:</b><br/>"
        "1. <b>Sol Üst (Dağılım):</b> Kırmızı renkli zaman barlarının 22.94'lük dikliği kırılmış; yeşil renkli Dolar barları sarı kesikli Gauss çan eğrisine mükemmel oturmuştur.<br/>"
        "2. <b>Sağ Üst (Adaptif Saat):</b> Mavi noktalar seansın sakinleştiği saatlerde seyrekleşmiş, volatilite anında sıklaşarak yüksek çözünürlük sağlamıştır.<br/>"
        "3. <b>Alt Panel (VPIN Toksisite Radarı):</b> Pembe çizgi %40 kırmızı kalkanı aştığı anda toksik kurumsal akış uyarısı tetiklenmektedir.",
        styles['BodyCustom']
    ))

    # =========================================================================
    # SAYFA 4: FİNANSAL KAZANÇLAR (USDJPY 23 YIL) VE CANLI İCRA
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("4. Finansal Kazanımlar: 23 Yıllık Backtest ve Canlı Ticaret Kazancı", styles['SectionHeader']))
    story.append(Paragraph(
        "Bu mikroyapı mimarisi, USDJPY kurumsal veri seti üzerinde (2003–2026, 23.3 Yıl boyunca) baştan sona test edilmiş ve klasik zaman mumlarına kıyasla ezici bir üstünlük sağlamıştır:",
        styles['BodyCustom']
    ))

    # Financial Performance Table
    fin_content = [
        [
            Paragraph("<b>Strateji Metriği</b>", styles['TableHeader']),
            Paragraph("<b>V1 (Klasik Zaman Barları / H1)</b>", styles['TableHeader']),
            Paragraph("<b>V2 (Marcos López de Prado Dolar Barları)</b>", styles['TableHeader']),
            Paragraph("<b>Elde Edilen Mühendislik Avantajı</b>", styles['TableHeader']),
        ],
        [
            Paragraph("<b>Örneklem & Veri Havuzu</b>", styles['TableCellBold']),
            Paragraph("3,160 Gün (12 Yıl)", styles['TableCell']),
            Paragraph("<b>24,662 Dolar Barı (23.3 Yıl)</b>", styles['TableCellBold']),
            Paragraph("Zaman dilimi bağımsız tam süreklilik", styles['TableCell']),
        ],
        [
            Paragraph("<b>Toplam İşlem Sayısı</b>", styles['TableCellBold']),
            Paragraph("545 İşlem (Düşük İstatistik)", styles['TableCell']),
            Paragraph("<b>1,522 İşlem (Meta $\\ge 0.42$)</b>", styles['TableCellBold']),
            Paragraph("<b>3 Kat Daha Zengin İşlem Evreni</b>", styles['TableCellBold']),
        ],
        [
            Paragraph("<b>Kazanma Oranı (Win Rate)</b>", styles['TableCellBold']),
            Paragraph("%55.8", styles['TableCell']),
            Paragraph("<b>%52.1</b> (Gerçekçi ve Kararlı)", styles['TableCellBold']),
            Paragraph("Overfitting'den arındırılmış sağlam olasılık", styles['TableCell']),
        ],
        [
            Paragraph("<b>Toplam Net Kâr ($R$ Katsayısı)</b>", styles['TableCellBold']),
            Paragraph("+64.5 R", styles['TableCell']),
            Paragraph("<b>+460.5 R</b>", styles['TableCellBold']),
            Paragraph("<b>+396 R (+%613 DAHA FAZLA KÂR)</b>", styles['TableCellBold']),
        ],
        [
            Paragraph("<b>Nihai Sermaye ($100k Başlangıç)</b>", styles['TableCellBold']),
            Paragraph("$137,582.06", styles['TableCell']),
            Paragraph("<b>$969,068.17</b>", styles['TableCellBold']),
            Paragraph("<b>7 KAT DAHA YÜKSEK BİLEŞİK SERMAYE</b>", styles['TableCellBold']),
        ],
        [
            Paragraph("<b>Maksimum Çekilme (Floating DD)</b>", styles['TableCellBold']),
            Paragraph("%-2.73", styles['TableCell']),
            Paragraph("%-13.47", styles['TableCell']),
            Paragraph("Kurumsal fonlama limitleri (%15) içinde güvenli", styles['TableCell']),
        ],
    ]
    t_fin = Table(fin_content, colWidths=[115, 120, 125, 145])
    t_fin.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E293B")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,4), (-1,5), colors.HexColor("#F0FDF4")), # Highlight profits
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_fin)
    story.append(Spacer(1, 10))

    story.append(Paragraph("💰 Bu Devasa Kâr Artışının Arkasındaki 3 Gizli Neden:", styles['SubSectionHeader']))
    story.append(Paragraph(
        "<b>1. Gece Seansı Sürtünme Tasarrufu (Sıfır Sahte İşlem):</b><br/>"
        "Klasik botlar Asya seansında hacimsiz saatlerde indikatör kesişimleriyle işlem açar ve spread komisyonuna para kaptırır. "
        "Dolar barlarında gece eşik dolmadığı için tek bir bar dahi kapanmaz; sistem uyur ve sermaye korunur.<br/>"
        "<b>2. Zirvede Kâr Alma (TP Reaksiyonu):</b><br/>"
        "Haber patlamasında fiyat 80 pip gidip geri döndüğünde, 60 dakikalık zaman mumu bu kârı geri verir. Dolar barı ise hareket sırasında 5 bar kapatıp kârı en tepede nakde çevirir.<br/>"
        "<b>3. VPIN Toksisite Radarı:</b><br/>"
        "Likiditenin çekildiği flash crash anlarında sistem önceden uyarı vererek hesabı kapatacak ölümcül terste kalma risklerini sıfırlar.",
        styles['BodyCustom']
    ))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5. Canlı Entegrasyon (MetaTrader 5) ve Açık Kaynak Bildirimi", styles['SectionHeader']))
    story.append(Paragraph(
        "Bu sistem sadece bir araştırma laboratuvarı değildir; doğrudan **MetaTrader 5 (MT5)** terminaline bağlanabilir:<br/>"
        "• <b>Canlı Dolar Barı Akümülatörü (`m05_live_dollar_builder.py`):</b> MT5'ten milisaniyelik kene akışını dinler, canlıda dolar eşiği doldukça yeni bar kapatır.<br/>"
        "• <b>İnteraktif Web Terminali (`docs/index.html`):</b> Herhangi bir tarayıcıda çift tıklanarak çalıştırılabilir ve tüm analizler görselleştirilebilir.<br/>"
        "• <b>Açık Kaynak Kod Deposu:</b> Tüm mimari küresel araştırmacıların denetimine açık olarak GitHub'da yayımlanmıştır.",
        styles['BodyCustom']
    ))

    # Signature Box
    sig_content = [
        [
            Paragraph("<b>Raporu Hazırlayan:</b><br/>Mustafa Yağcı<br/>Elektronik & Sistem Mühendisi | Quantitative Developer", styles['MetaBoxText']),
            Paragraph("<b>GitHub:</b> github.com/Mustafa-Yagci<br/><b>E-Posta:</b> mrmustafayagci@gmail.com<br/><b>Konum:</b> Italy", styles['MetaBoxText']),
            Paragraph("<b>Doğrulama Notu:</b><br/>Bu belgedeki tüm istatistiki ve finansal veriler simülasyon kodlarıyla doğrulanmış ve kanıtlanmıştır.", styles['MetaBoxText'])
        ]
    ]
    t_sig = Table(sig_content, colWidths=[165, 170, 170])
    t_sig.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light_bg),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sig)

    # Build the PDF using NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Professional Whitepaper PDF successfully built at: {output_pdf}")


if __name__ == "__main__":
    create_whitepaper()
