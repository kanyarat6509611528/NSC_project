from django import forms

class SelfTestForm(forms.Form):
    QUESTION_CHOICES = [
        ('0', 'ไม่เคยเลย'),
        ('1', 'แทบไม่เคย'),
        ('2', 'เป็นบางครั้ง'),
        ('3', 'เกือบตลอดเวลา'),
        ('4', 'ตลอดเวลา'),
    ]

    question_1 = forms.ChoiceField(choices=QUESTION_CHOICES, widget=forms.RadioSelect, label="1. ฉันรู้สึกหวาดกลัวอย่างรุนแรง ฉับพลัน หรือตกใจในสถานการณ์เหล่านี้")
    question_2 = forms.ChoiceField(choices=QUESTION_CHOICES, widget=forms.RadioSelect, label="2. ฉันรู้สึกวิตกกังวล กระวนกระวาย หรือประหม่าเกี่ยวกับสถานการณ์เหล่านี้")
    question_3 = forms.ChoiceField(choices=QUESTION_CHOICES, widget=forms.RadioSelect, label="3. ฉันเคยคิดว่าตัวเองจะได้รับบาดเจ็บ กลัวจนควบคุมไม่ได้ หรือคิดว่าจะมีเรื่องเลวร้ายเกิดขึ้นในสถานการณ์เหล่านี้")
    question_4 = forms.ChoiceField(choices=QUESTION_CHOICES, widget=forms.RadioSelect, label="4. หัวใจฉันเต้นเร็ว เหงื่อออก ใจสั่น จะเป็นลม หรือตัวสั่นในสถานการณ์เหล่านี้")
    question_5 = forms.ChoiceField(choices=QUESTION_CHOICES, widget=forms.RadioSelect, label="5. ฉันรู้สึกกล้ามเนื้อตึงเครียด รู้สึกกระวนกระวาย หรือไม่สามารถผ่อนคลายได้ในสถานการณ์เหล่านี้")
    question_6 = forms.ChoiceField(choices=QUESTION_CHOICES, widget=forms.RadioSelect, label="6. ฉันหลีกเลี่ยง ไม่เข้าใกล้ หรือไม่ยอมเข้าไปในสถานการณ์เหล่านี้")
    question_7 = forms.ChoiceField(choices=QUESTION_CHOICES, widget=forms.RadioSelect, label="7. ฉันพยายามหลีกเลี่ยงสถานการณ์เหล่านี้ หรือออกมาก่อน")
    question_8 = forms.ChoiceField(choices=QUESTION_CHOICES, widget=forms.RadioSelect, label="8. ฉันใช้เวลาอย่างมากในการเตรียมตัว หรือผัดวันประกันพรุ่งเพื่อเผชิญกับสถานการณ์เหล่านี้")
    question_9 = forms.ChoiceField(choices=QUESTION_CHOICES, widget=forms.RadioSelect, label="9. ฉันเบี่ยงเบนความสนใจตัวเองเพื่อไม่ให้คิดถึงสถานการณ์เหล่านี้")
    question_10 = forms.ChoiceField(choices=QUESTION_CHOICES, widget=forms.RadioSelect, label="10. ฉันต้องการความช่วยเหลือเพื่อรับมือกับสถานการณ์เหล่านี้ (เช่น เครื่องดื่มแอลกอฮอล์ ยา วัตถุมงคล บุคคลอื่น)")




