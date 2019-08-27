import os
import parse


class Files:  # 跨文件统计
    def __init__(self, url=r'C:\Users\liyu\Desktop\文言文', grade1=0, grade2=200):  # 年级筛选左右均为闭区间
        self.url = url
        self.grade1 = grade1
        self.grade2 = grade2
        self.all_data = self.search()

    def get_files_url(self):
        fin_list = []
        filenames = os.listdir(self.url)
        for name in filenames:
            if name != '语法规则.txt':
                file_url = os.path.join(self.url, name)
                fin_list.append(file_url)
        return fin_list

    def search(self, *args, **kw):  # 跨文章查询，指定属性，不包含年级
        file_urls = self.get_files_url()
        fin_list = []
        fin_fin_list = []
        grade1 = self.grade1
        grade2 = self.grade2
        for url in file_urls:
            file = parse.File(url)
            if file.grade >= grade1 and file.grade <= grade2:
                temp_file = file.find2(*args, **kw)
                for ch1 in temp_file:
                    ch1['作者'] = file.author
                    ch1['朝代'] = file.dynasty
                    ch1['出处'] = file.origin
                    ch1['标题'] = file.title
                    ch1['年级'] = file.grade
                fin_list += temp_file

        for dicx in fin_list:
            fin_fin_list.append(ParseTypeAttrs(dicx).get_data())

        return fin_fin_list


class ParseTypeAttrs:  # 具体解释一些属性，例如实词u类型的"解释"属性是由用法决定的，应该把"古今异义"的"解释"属性解释为"今义"
    def __init__(self, raw_dic):
        self.raw_dic = raw_dic
        self.tp = raw_dic['type']
        if self.tp == 'u':
            self.parse_u()
        elif self.tp == 'o':
            self.parse_o()
        else:
            pass

    def parse_u(self):
        if '用法' in self.raw_dic.keys() and self.raw_dic['用法'] == '古今异义':
            self.raw_dic['今义'] = self.raw_dic['解释']
            del self.raw_dic['解释']
        elif '用法' in self.raw_dic.keys() and self.raw_dic['用法'] == '形容→名':
            self.raw_dic['原义'] = self.raw_dic['解释']
            del self.raw_dic['解释']
        elif '用法' in self.raw_dic.keys() and self.raw_dic['用法'] == '动→名':
            self.raw_dic['原义'] = self.raw_dic['解释']
            del self.raw_dic['解释']
        elif '用法' in self.raw_dic.keys() and self.raw_dic['用法'] == '名→动':
            self.raw_dic['原义'] = self.raw_dic['解释']
            del self.raw_dic['解释']
        elif '用法' in self.raw_dic.keys() and self.raw_dic['用法'] == '名→状':
            self.raw_dic['原义'] = self.raw_dic['解释']
            del self.raw_dic['解释']
        elif '用法' in self.raw_dic.keys() and self.raw_dic['用法'] == '通假字':
            self.raw_dic['原义'] = self.raw_dic['解释']
            del self.raw_dic['解释']
        else:
            pass

    def parse_o(self):
        pass

    def get_data(self):
        return self.raw_dic


# f = Files(r'C:\Users\liyu\Desktop\文言文', 0, 81)
#
# for ch in f.all_data:
#     print(ch)
