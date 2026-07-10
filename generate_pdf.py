import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Don't draw header/footer on page 1 (cover style)
        if self._pageNumber == 1:
            self.restoreState()
            return
            
        # Fonts & colors
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header text
        self.drawString(54, 750, "SQL QUIZ ANSWERS & DETAILED EXPLANATIONS")
        
        # Header line
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.75)
        self.line(54, 742, 558, 742)
        
        # Footer line
        self.line(54, 52, 558, 52)
        
        # Footer text
        self.setFont("Helvetica", 8)
        self.drawString(54, 38, "Oracle SQL Practice Questions")
        self.drawRightString(558, 38, f"Page {self._pageNumber} of {page_count}")
        
        self.restoreState()

def create_pdf(output_path):
    # Setup document
    # topMargin=70 to start below the header line at 742
    # bottomMargin=70 to stop above the footer line at 52
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=70,
        bottomMargin=70
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#1A365D'),
        spaceAfter=8
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=25
    )
    
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#718096'),
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2C5282'),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    q_title_style = ParagraphStyle(
        'QuestionTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1A202C'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    code_style = ParagraphStyle(
        'CodeText',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#2D3748')
    )
    
    opt_style = ParagraphStyle(
        'OptionText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#4A5568'),
        leftIndent=15,
        spaceAfter=3
    )
    
    opt_correct_style = ParagraphStyle(
        'OptionCorrectText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#276749'),
        leftIndent=15,
        spaceAfter=3
    )
    
    ans_style = ParagraphStyle(
        'AnswerText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#22543D'),
        spaceBefore=4,
        spaceAfter=4,
        keepWithNext=True
    )
    
    exp_style = ParagraphStyle(
        'ExplanationText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=12
    )

    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=10
    )

    story = []
    
    # ------------------ COVER PAGE / HEADER ------------------
    story.append(Spacer(1, 40))
    story.append(Paragraph("Oracle SQL Practice Quiz", title_style))
    story.append(Paragraph("Complete Questions, Correct Answers &amp; Detailed Explanations", subtitle_style))
    
    # Info card table
    info_data = [
        [Paragraph("<b>Topic:</b> Database Systems &amp; Oracle SQL", body_style), 
         Paragraph("<b>Date:</b> July 2026", body_style)],
        [Paragraph("<b>Questions Analyzed:</b> 15 (Q9 Missing)", body_style), 
         Paragraph("<b>Format:</b> Multiple Choice (MCQ)", body_style)]
    ]
    info_table = Table(info_data, colWidths=[240, 240])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#EDF2F7')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor('#CBD5E0')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("This document contains verified answers and comprehensive technical explanations for the SQL practice quiz. Each question has been analyzed according to standard Oracle SQL behaviors.", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("<i>Scroll down or print to view all answers page by page.</i>", meta_style))
    story.append(PageBreak())
    
    # ------------------ QUESTIONS ------------------
    
    questions = [
        # Q1
        {
            "num": 1,
            "q": "Which clause is executed first in a SQL query?",
            "code": "SELECT *\nFROM Employee\nWHERE salary > 50000\nORDER BY salary;",
            "options": [
                ("A", "SELECT", False),
                ("B", "ORDER BY", False),
                ("C", "FROM", True),
                ("D", "WHERE", False)
            ],
            "correct_letter": "C",
            "correct_text": "FROM",
            "exp": "In SQL, the logical order of query execution begins with identifying the source data source(s). The <b>FROM</b> clause is executed first. The database must determine which table is being queried before filtering rows or selecting columns. The execution sequence for this query is:<br/>1. <b>FROM</b> Employee (identifies source table)<br/>2. <b>WHERE</b> salary &gt; 50000 (filters rows)<br/>3. <b>SELECT</b> * (projects/retrieves columns)<br/>4. <b>ORDER BY</b> salary (sorts the final results)"
        },
        # Q2
        {
            "num": 2,
            "q": "Which command removes all rows from a table but keeps the structure?",
            "options": [
                ("A", "DROP", False),
                ("B", "DELETE", False),
                ("C", "REMOVE", False),
                ("D", "TRUNCATE", True)
            ],
            "correct_letter": "D",
            "correct_text": "TRUNCATE",
            "exp": "<b>TRUNCATE TABLE</b> is a DDL (Data Definition Language) command that removes all rows from a table by deallocating the database data pages used to store the table data. Since it operates at the physical level, it is extremely fast and uses minimal transaction log space compared to <b>DELETE</b>. It leaves the table structure, columns, constraints, and indexes intact. Note that <b>DELETE</b> without a WHERE clause also achieves this but is a slower DML command that processes rows individually."
        },
        # Q3
        {
            "num": 3,
            "q": "Which function returns the first non-null value in Oracle?",
            "options": [
                ("A", "NVL", False),
                ("B", "DECODE", False),
                ("C", "COALESCE", True),
                ("D", "NULLIF", False)
            ],
            "correct_letter": "C",
            "correct_text": "COALESCE",
            "exp": "The <b>COALESCE</b> function is a standard SQL function that evaluates arguments in order and returns the first non-null value in the list. Unlike <b>NVL</b>, which only accepts exactly two arguments, <b>COALESCE</b> can accept any number of arguments: <i>COALESCE(expr1, expr2, ..., exprN)</i>. <b>DECODE</b> is an Oracle-specific conditional statement, and <b>NULLIF</b> returns null if two arguments are equal."
        },
        # Q4
        {
            "num": 4,
            "q": "What is the output?",
            "code": "SELECT NVL(NULL, 100) FROM DUAL;",
            "options": [
                ("A", "NULL", False),
                ("B", "0", False),
                ("C", "100", True),
                ("D", "Error", False)
            ],
            "correct_letter": "C",
            "correct_text": "100",
            "exp": "The <b>NVL(expr1, expr2)</b> function replaces a null value with a default value. If <i>expr1</i> is NULL, it returns <i>expr2</i>; otherwise, it returns <i>expr1</i>. In this query, the first argument is NULL, so the function returns the second argument: <b>100</b>."
        },
        # Q5
        {
            "num": 5,
            "q": "Which join returns all matching rows plus unmatched rows from both tables?",
            "options": [
                ("A", "INNER JOIN", False),
                ("B", "LEFT JOIN", False),
                ("C", "RIGHT JOIN", False),
                ("D", "FULL OUTER JOIN", True)
            ],
            "correct_letter": "D",
            "correct_text": "FULL OUTER JOIN",
            "exp": "A <b>FULL OUTER JOIN</b> (or simply FULL JOIN) retrieves all matched rows from both tables, plus all unmatched rows from the left table (padded with NULLs for right columns) and all unmatched rows from the right table (padded with NULLs for left columns)."
        },
        # Q6
        {
            "num": 6,
            "q": "Which operator is used for pattern matching?",
            "options": [
                ("A", "MATCH", False),
                ("B", "LIKE", True),
                ("C", "IN", False),
                ("D", "BETWEEN", False)
            ],
            "correct_letter": "B",
            "correct_text": "LIKE",
            "exp": "The <b>LIKE</b> operator is used in a WHERE clause to perform wildcard pattern matching. It uses two wildcard symbols: <b>%</b> (matches zero or more characters) and <b>_</b> (matches exactly one character). <i>MATCH</i> is not a standard SQL operator for basic pattern matching; <i>IN</i> is for list membership; <i>BETWEEN</i> is for range filtering."
        },
        # Q7
        {
            "num": 7,
            "q": "What will be the output?",
            "code": "SELECT LENGTH('ORACLE SQL') FROM DUAL;",
            "options": [
                ("A", "9", False),
                ("B", "10", True),
                ("C", "11", False),
                ("D", "12", False)
            ],
            "correct_letter": "B",
            "correct_text": "10",
            "exp": "The <b>LENGTH(string)</b> function counts and returns the number of characters in a string. The string 'ORACLE SQL' has 10 characters in total:<br/>- 'ORACLE' (6 characters)<br/>- Space ' ' (1 character)<br/>- 'SQL' (3 characters)<br/>Total characters: 6 + 1 + 3 = 10. Thus, option B is correct."
        },
        # Q8
        {
            "num": 8,
            "q": "Which clause is used to filter grouped records?",
            "options": [
                ("A", "WHERE", False),
                ("B", "GROUP BY", False),
                ("C", "HAVING", True),
                ("D", "ORDER BY", False)
            ],
            "correct_letter": "C",
            "correct_text": "HAVING",
            "exp": "The <b>HAVING</b> clause filters records <i>after</i> they have been grouped using <b>GROUP BY</b>. The key difference is that the <b>WHERE</b> clause filters individual rows before grouping, and it cannot contain aggregate functions (like SUM, COUNT, AVG). The <b>HAVING</b> clause is designed specifically to filter group-level records based on aggregates."
        },
        # Q10
        {
            "num": 10,
            "q": "What is the output?",
            "code": "SELECT MOD(25,4) FROM DUAL;",
            "options": [
                ("A", "5", False),
                ("B", "6", False),
                ("C", "1", True),
                ("D", "4", False)
            ],
            "correct_letter": "C",
            "correct_text": "1",
            "exp": "The <b>MOD(n2, n1)</b> function returns the remainder of <i>n2</i> divided by <i>n1</i>. In this case, 25 divided by 4 is 6 with a remainder of <b>1</b>. Therefore, MOD(25, 4) evaluates to 1."
        },
        # Q11
        {
            "num": 11,
            "q": "Which function returns the current system date?",
            "options": [
                ("A", "GETDATE()", False),
                ("B", "CURRENT_DATE()", False),
                ("C", "SYSDATE", True),
                ("D", "TODAY()", False)
            ],
            "correct_letter": "C",
            "correct_text": "SYSDATE",
            "exp": "In Oracle SQL (which is the database context established by the use of the <b>DUAL</b> table in other questions), <b>SYSDATE</b> is the standard built-in function that returns the current system date and time. Crucially, in Oracle, <b>SYSDATE</b> is used as a pseudo-column without parentheses. <i>GETDATE()</i> is Microsoft SQL Server's equivalent function, and <i>TODAY()</i> is used in Informix."
        },
        # Q12
        {
            "num": 12,
            "q": "What is the output?",
            "code": "SELECT ROUND(123.456, 1) FROM DUAL;",
            "options": [
                ("A", "123.4", False),
                ("B", "123.5", True),
                ("C", "123.46", False),
                ("D", "124", False)
            ],
            "correct_letter": "B",
            "correct_text": "123.5",
            "exp": "The <b>ROUND(number, decimal_places)</b> function rounds a numeric value to the specified number of decimal places. Here, 123.456 is rounded to 1 decimal place. The digit in the second decimal place (5) is &gt;= 5, which triggers rounding up of the first decimal digit (4) to 5, resulting in <b>123.5</b>."
        },
        # Q13
        {
            "num": 13,
            "q": "Which query finds the second highest salary?",
            "options": [
                ("A", "SELECT MAX(SAL) FROM EMP;", False),
                ("B", "SELECT MAX(SAL) FROM EMP WHERE SAL < (SELECT MAX(SAL) FROM EMP);", True),
                ("C", "SELECT MIN(SAL) FROM EMP;", False),
                ("D", "SELECT AVG(SAL) FROM EMP;", False)
            ],
            "correct_letter": "B",
            "correct_text": "B",
            "exp": "Option B uses a subquery to find the maximum salary in the table: <i>(SELECT MAX(SAL) FROM EMP)</i>. The outer query then finds the maximum salary from the set of salaries that are strictly less than that absolute maximum. This effectively yields the second highest salary."
        },
        # Q14
        {
            "num": 14,
            "q": "Which statement about indexes is true?",
            "options": [
                ("A", "Improve query performance", True),
                ("B", "Store duplicate tables", False),
                ("C", "Reduce table size", False),
                ("D", "Replace constraints", False)
            ],
            "correct_letter": "A",
            "correct_text": "Improve query performance",
            "exp": "Indexes are database structures that speed up the retrieval of data rows from tables (improving SELECT query performance). They act like an index in a book. However, they do not reduce table size (they consume extra storage space) and do not store entire duplicate tables."
        },
        # Q15
        {
            "num": 15,
            "q": "Where can a SQL Function be used?",
            "options": [
                ("A", "Inside SELECT statement", False),
                ("B", "Inside WHERE clause", False),
                ("C", "Inside ORDER BY clause", False),
                ("D", "All of the above", True)
            ],
            "correct_letter": "D",
            "correct_text": "All of the above",
            "exp": "SQL single-row functions (like UPPER, ROUND, NVL) can be used in the <b>SELECT</b> list to format outputs, in the <b>WHERE</b> clause to filter rows based on conditions (e.g. <i>WHERE LOWER(name) = 'alice'</i>), and in the <b>ORDER BY</b> clause to sort rows based on a transformed value (e.g. <i>ORDER BY LENGTH(name)</i>)."
        }
    ]
    
    # Loop over questions to append to story
    for q_item in questions:
        q_elements = []
        
        # Heading
        q_num = q_item["num"]
        q_text = q_item["q"]
        q_elements.append(Paragraph(f"Question {q_num}: {q_text}", q_title_style))
        
        # Code block if present
        if "code" in q_item:
            code_html = q_item["code"].replace("\n", "<br/>").replace(" ", "&nbsp;")
            code_p = Paragraph(f"<code>{code_html}</code>", code_style)
            code_table = Table([[code_p]], colWidths=[490])
            code_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F7FAFC')),
                ('PADDING', (0,0), (-1,-1), 8),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ]))
            q_elements.append(code_table)
            q_elements.append(Spacer(1, 6))
            
        # Options list
        for l, text, is_correct in q_item["options"]:
            if is_correct:
                opt_html = f"<b>({l}) {text} &nbsp;&nbsp;&nbsp;&nbsp;[CORRECT]</b>"
                q_elements.append(Paragraph(opt_html, opt_correct_style))
            else:
                opt_html = f"({l}) {text}"
                q_elements.append(Paragraph(opt_html, opt_style))
                
        # Correct answer line
        q_elements.append(Spacer(1, 4))
        correct_letter = q_item["correct_letter"]
        correct_text = q_item["correct_text"]
        ans_box_text = f"Correct Answer: {correct_letter}) {correct_text}" if correct_letter != correct_text else f"Correct Answer: Option {correct_letter}"
        q_elements.append(Paragraph(ans_box_text, ans_style))
        
        # Explanation
        exp_html = f"<b>Explanation:</b> {q_item['exp']}"
        q_elements.append(Paragraph(exp_html, exp_style))
        
        # Divider line
        divider_data = [[""]]
        divider_table = Table(divider_data, colWidths=[500])
        divider_table.setStyle(TableStyle([
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ]))
        q_elements.append(divider_table)
        q_elements.append(Spacer(1, 10))
        
        # Keep each question block together so it doesn't break awkwardly across pages
        story.append(KeepTogether(q_elements))
        
        # Add a manual separator/spacer
        story.append(Spacer(1, 10))
        
    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully built at: {output_path}")

if __name__ == "__main__":
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "sql_quiz_answers.pdf")
    create_pdf(pdf_path)
