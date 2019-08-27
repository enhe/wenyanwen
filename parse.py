# 都要增加一项，所在的句子

class DefaultAttrs:
    def __init__(self, typeclass):
        self.typeclass = typeclass
        self.data = ''
        self.parse()

    def parse(self):
        if self.typeclass == 'm':
            self.data = '义'
        elif self.typeclass == 'o':
            self.data = '被省略的词语'
        elif self.typeclass == 'u':
            self.data = '义'
        elif self.typeclass == 'f':
            self.data = '句式含义'
        elif self.typeclass == 'b':
            self.data = '被动句'
        elif self.typeclass == 'y':
            self.data = '判断句式结构'
        else:
            print('%s没有默认属性，请检查属性名称' % self.typeclass)


class SingleNode:
    def __init__(self, raw_sentence, context):  # 传入原始文本，包含单尖括号
        self.context = context
        self.raw_sentence = raw_sentence[1:-2].split()  # 把原始句子断开为列表
        self.data = {}
        self.data['type'] = self.raw_sentence[0]
        self.data['context'] = ''
        for ch in self.raw_sentence[1:]:
            if ch.find('：') > -1:
                ch_temp = ch.split('：')
                self.data[ch_temp[0]] = ch_temp[1]
            else:
                self.data[DefaultAttrs(self.data['type']).data] = ch
        self.get_context()

    def get_data(self):
        return self.data

    def get_type(self):
        return self.data['type']

    def get_context(self):
        if self.data['type'] == 'o':
            fin_str1 = ''
            head_p = 0
            end_p = 0
            cnt1 = 0  # 记录总字符顺序
            cnt2 = 0  # 记录<符号后面的字符顺序
            for ch in self.context:
                if ch == '<':
                    head_p += 1
                    fin_str1 += '('
                    cnt2 = cnt1
                elif ch == '>':
                    end_p += 1
                    fin_str1 += ')'
                else:
                    if head_p == 0 or (head_p == 1 and end_p == 1):
                        fin_str1 += ch
                    else:
                        if cnt1 - cnt2 == 1:
                            fin_str1 += self.data['被省略的词语']
                        else:
                            pass
                cnt1 += 1
            self.data['context'] = fin_str1
        else:
            self.data['context'] = self.get_clean_p(self.context)

    def get_clean_p(self, p):  # 获得清除所有标记后的原文
        fin_str = ''
        count_head = 0
        count_end = 0
        for ch in p:
            if ch == '<':
                count_head += 1
            elif ch == '>':
                count_end += 1
            else:
                if count_head == count_end:
                    fin_str += ch
        return fin_str


class DoubleNode:
    def __init__(self, raw_sentence, context):  # 传入双尖括号、属性及原文
        self.data = {}
        self.raw_sentence = raw_sentence
        self.cut_sentence = self.cut_raw()
        self.parse_atr()
        self.parse_raw_sentence()
        self.data['context'] = context

    def cut_raw(self):
        one_block = ''
        two_block = ''
        count_head = 0
        count_end = 0
        for ch in self.raw_sentence:
            if ch == '<':
                count_head += 1
                if count_head == 1:
                    one_block += ch
            elif ch == '>':
                count_end += 1
                if count_end == 1:
                    one_block += ch
            elif count_head == 1 and count_end < 1:
                one_block += ch
            elif count_head == 1 and count_end == 1:
                two_block += ch
        return one_block, two_block

    def parse_atr(self):  # 分析前尖括号内的属性
        one_block = self.cut_sentence[0][1:-1].split()
        self.data['type'] = one_block[0]
        for ch in one_block[1:]:
            if ch.find('：') > -1:
                ch_temp = ch.split('：')
                self.data[ch_temp[0]] = ch_temp[1]
            else:
                self.data[DefaultAttrs(self.data['type']).data] = ch

    def parse_raw_sentence(self):  # 分离原文
        self.data['raw_sentence'] = self.cut_sentence[1]


class File:
    def __init__(self, f_root):
        self.raw_file = open(f_root, 'rt', encoding="utf-8").readlines()
        self.node_list = []
        self.handle_ps()
        self.get_t_file()
        self.grade = 0
        self.author = ''
        self.title = ''
        self.dynasty = ''
        self.origin = ''
        self.append_info()

    def get_t_file(self):  # 获取t标签的部分，包含标题、作者、朝代、适用年级、课内课外等信息
        for p in self.raw_file:
            target_p = p[0:2]
            if target_p == '<t':
                self.node_list.append(DoubleNode(p.strip(), ''))

    def get_p_file(self):  # 删除非p标签的部分，即筛选出文本正文，包含标记信息
        p_file = []
        for p in self.raw_file:
            target_p = p[0:3]
            if target_p == '<p>':
                p_end = p.find('</p>')
                p_file.append(p[3:p_end])
        return p_file

    def handle_ps(self):  # 处理段落，解析标记信息，按照段落解析
        ps = self.get_p_file()

        for p in ps:
            self.handle_p(p)

    def handle_p(self, p):  # 处理段落，为node_list绑定数据
        ch_count = 0
        for ch in p:
            if ch == '<':
                # 先判断是单标还是双标，如果是双标，要判断是前标还是后标
                p_sign_end = p[ch_count:].find('>') + ch_count  # 找到最近的后尖括号

                if p[ch_count:p_sign_end + 1].find('/') > -1 and p[ch_count:p_sign_end + 1].find(
                        ' ') > -1:  # 如果后尖括号之前有斜线，且后尖括号与前尖括号之间的内容含空格，则是单标
                    target_p = p[ch_count:p_sign_end + 1]  # 单表尖括号里及其内容

                    self.node_list.append(SingleNode(target_p, self.get_context_single(p, ch_count)))
                elif p[ch_count:p_sign_end + 1].find('/') > -1 and p[ch_count:p_sign_end + 1].find(
                        ' ') == -1:  # 如果后尖括号之前有斜线，且后尖括号与前尖括号之间的内容不包含空格，则是双标的后标
                    # print(p[ch_count:p_sign_end + 1])
                    pass
                else:  # 双标的前标
                    # 根据双标的前标来寻找双标的后标
                    type_sign = p[ch_count + 1:ch_count + 2]
                    target_after = '</' + type_sign + '>'
                    target_head = '<' + type_sign
                    p_after_sign = p[ch_count:].find(target_after) + ch_count  # 后标指针
                    count_sim_sign = p[ch_count:p_after_sign].count(target_head)
                    if count_sim_sign == 1:  # 没有嵌套情况
                        pp = p[ch_count:p_after_sign + 4]
                        fin_str = ''
                        sum_ch = len(pp)
                        count_ch = 0
                        count_head = 0
                        count_after = 0
                        for ch1 in pp:
                            count_ch += 1
                            if ch1 == "<":
                                count_head += 1
                            elif ch1 == ">":
                                count_after += 1

                            if count_head == count_after:
                                if ch1 == ">":
                                    if count_head == 1 or count_ch == sum_ch:
                                        fin_str += ch1
                                    else:
                                        pass
                                else:
                                    fin_str += ch1
                            elif count_after < count_head:
                                if count_head == 1:
                                    fin_str += ch1
                                else:
                                    if count_ch >= sum_ch - 4:
                                        fin_str += ch1
                                    else:
                                        pass
                        self.node_list.append(DoubleNode(fin_str, self.get_context_double(p, ch_count)))
                    else:  # 有嵌套情况
                        p_start = p_after_sign
                        for ch in range(count_sim_sign - 1):
                            p_start = p[p_start + 4:].find(target_after) + p_start + 4
                        pp = p[ch_count: p_start + 4]  # 要清除内部嵌套的尖括号
                        fin_str = ''
                        sum_ch = len(pp)
                        count_ch = 0
                        count_head = 0
                        count_after = 0
                        for ch1 in pp:
                            count_ch += 1
                            if ch1 == "<":
                                count_head += 1
                            elif ch1 == ">":
                                count_after += 1

                            if count_head == count_after:
                                if ch1 == ">":
                                    if count_head == 1 or count_ch == sum_ch:
                                        fin_str += ch1
                                    else:
                                        pass
                                else:
                                    fin_str += ch1
                            elif count_after < count_head:
                                if count_head == 1:
                                    fin_str += ch1
                                else:
                                    if count_ch >= sum_ch - 4:
                                        fin_str += ch1
                                    else:
                                        pass
                        self.node_list.append(DoubleNode(fin_str, self.get_context_double(p, ch_count)))
            ch_count += 1

    def get_context_double(self, p, cnt):  # 为双尖括号服务
        biaodian = ['，', '。', '！', '“', '”', '‘', '’', '：', '？']

        p_start = cnt
        p_end = cnt

        flag_start = 0  # 前指针结束标识
        flag_end = 0  # 后指针结束标识

        cnt_start_1 = 0  # 前指针经历的 < 数量
        cnt_start_2 = 0  # 前指针经历的 > 数量

        cnt_end_1 = 0  # 后指针经历的 < 数量
        cnt_end_2 = 0  # 后指针经历的 > 数量

        while True:
            if flag_start == 0:
                if p_start == 0:
                    flag_start = 1

                if p[p_start] == '<':
                    cnt_start_1 += 1
                    p_start -= 1
                elif p[p_start] == '>':
                    cnt_start_2 += 1
                    p_start -= 1
                else:
                    if cnt_start_1 - cnt_start_2 == 0:
                        p_start -= 1
                    else:
                        if p[p_start] in biaodian:
                            flag_start = 1
                        else:
                            p_start -= 1
            else:
                if p[p_start] in biaodian:
                    p_start += 1
                break

        while True:
            if flag_end == 0:
                if p[p_end] == '<':
                    cnt_end_1 += 1
                    p_end += 1
                elif p[p_end] == '>':
                    cnt_end_2 += 1
                    p_end += 1
                else:
                    if cnt_end_1 - cnt_end_2 == 1:
                        p_end += 1
                    else:
                        if cnt_end_1 == 1:
                            p_end += 1
                        else:
                            if p[p_end] in biaodian:
                                flag_end = 1
                            else:
                                p_end += 1
            else:
                break

        fin_str = self.get_clean_p(p[p_start:p_end])

        return fin_str

    def get_context_single(self, p, cnt):  # 为单尖括号服务，输出结果为所在句子中仅含此单尖括号
        biaodian = ['，', '。', '！', '“', '”', '‘', '’', '：', '？']

        p_start = cnt
        p_end = cnt

        flag_start = 0  # 前指针结束标识
        flag_end = 0  # 后指针结束标识

        cnt_start_1 = 0  # 前指针经历的 < 数量
        cnt_start_2 = 0  # 前指针经历的 > 数量

        cnt_end_1 = 0  # 后指针经历的 < 数量
        cnt_end_2 = 0  # 后指针经历的 > 数量

        cnt_move = 0  # 前指针移动量

        while True:  # 从前尖括号开始往前遍历
            if flag_start == 0:
                if p_start == 0:
                    flag_start = 1

                if p[p_start] == '<':
                    cnt_start_1 += 1
                    p_start -= 1
                    cnt_move += 1
                elif p[p_start] == '>':
                    cnt_start_2 += 1
                    p_start -= 1
                    cnt_move += 1
                else:
                    if cnt_start_1 - cnt_start_2 == 0:
                        p_start -= 1
                        cnt_move += 1
                    else:
                        if p[p_start] in biaodian:
                            flag_start = 1
                        else:
                            p_start -= 1
                            cnt_move += 1
            else:
                if p[p_start] in biaodian:
                    p_start += 1
                    cnt_move -= 1
                break

        while True:  # 从后尖括号开始往后遍历
            if flag_end == 0:
                if p[p_end] == '<':
                    cnt_end_1 += 1
                    p_end += 1
                elif p[p_end] == '>':
                    cnt_end_2 += 1
                    p_end += 1
                else:
                    if cnt_end_1 - cnt_end_2 == 1:
                        p_end += 1
                    else:
                        if p[p_end] in biaodian:
                            flag_end = 1
                        else:
                            p_end += 1
            else:
                break

        fin_str = self.get_clean_p_single(p[p_start:p_end], cnt_move)
        return fin_str

    def get_clean_p(self, p):  # 获得清除所有标记后的原文
        fin_str = ''
        count_head = 0
        count_end = 0
        for ch in p:
            if ch == '<':
                count_head += 1
            elif ch == '>':
                count_end += 1
            else:
                if count_head == count_end:
                    fin_str += ch
        return fin_str

    def get_clean_p_single(self, p, new_cnt):  # 获得清除所有标记后的原文，但保留new_cnt指针指向的尖括号

        fin_str = ''
        count_head = 0
        count_end = 0

        cnt = 0

        cnt_new_end = p[new_cnt:].find('>') + new_cnt  # new_cnt指针后最近的后尖括号位置

        for ch in p:
            if cnt >= new_cnt and cnt <= cnt_new_end:
                fin_str += ch
            else:
                if ch == '<':
                    count_head += 1
                elif ch == '>':
                    count_end += 1
                elif count_head == count_end:
                    fin_str += ch
            cnt += 1
        return fin_str

    def get_data(self):
        return self.node_list

    def find(self, **kw):
        data = self.get_data()
        fin_list = []
        for ch in data:
            ch_data = ch.data
            flag = 0
            for k, v in kw.items():
                if k in ch_data:
                    if ch_data[k] == v:
                        pass
                    else:
                        flag = 1
                else:
                    flag = 1
            if flag == 0:
                fin_list.append(ch_data)
        return fin_list

    def find2(self, *args, **kw):  # 固定某些属性，被固定的属性可以有赋值也可以没有，没有赋值时仅表明某条数据存在该属性，返回指定数据的列表
        data = self.get_data()
        fin_list = []
        for ch in data:
            flag = 1  # 指明指定属性是否存在，为0表示不存在
            ch = ch.data
            for i in args:
                if i not in ch.keys():
                    flag = 0
            for k, v in kw.items():
                if k not in ch.keys():
                    flag = 0
                else:
                    if v != ch[k]:
                        flag = 0
            if flag == 1:
                fin_list.append(ch)

        return fin_list

    def find_value(self, value, *args, **kw):  # 固定某些属性，被固定的属性可以有赋值也可以没有，没有赋值时仅表明某条数据存在该属性，查询指定属性的值的集合
        data = self.get_data()
        fin_set = set()
        for ch in data:
            flag = 1  # 指明指定属性是否存在，为0表示不存在
            flag_value = 0  # 记录有没有指定的待查属性
            ch = ch.data
            for i in args:
                if i not in ch.keys():
                    flag = 0
            for k, v in kw.items():
                if k not in ch.keys():
                    flag = 0
                else:
                    if v != ch[k]:
                        flag = 0
            if value in ch.keys():
                flag_value = 1
            if flag == 1 and flag_value == 1:
                fin_set.add(ch[value])
        return fin_set

    def classify(self):  # 每种type所具有的属性的公共集合
        fin_dic = {}
        data = self.get_data()
        for ch in data:
            ch = ch.data
            if ch['type'] == 't':
                pass
            else:
                if ch['type'] in fin_dic:
                    for k in ch.keys():
                        if k == 'type':
                            pass
                        else:
                            fin_dic[ch['type']].add(k)
                else:
                    fin_dic[ch['type']] = set()
                    for k in ch.keys():
                        if k == 'type':
                            pass
                        else:
                            fin_dic[ch['type']].add(k)

        return fin_dic

    def append_info(self):
        data = self.get_data()
        for ch in data:
            ch = ch.data
            if ch['type'] == 't':
                if '作者' in ch.keys():
                    self.author = ch['作者']
                if '年级' in ch.keys():
                    self.grade = int(ch['年级'])
                if 'raw_sentence' in ch.keys():
                    self.title = ch['raw_sentence']
                if '朝代' in ch.keys():
                    self.dynasty = ch['朝代']
                if '出处' in ch.keys():
                    self.origin = ch['出处']
                break

# file = File(r'C:\Users\liyu\Desktop\文言文\富贵不能淫.txt')
#
# for ch in file.find2():
#     print(ch)
