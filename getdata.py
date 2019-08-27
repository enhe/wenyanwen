import tongji as tj


class BaseSearch:  # 最灵活的查找
    def __init__(self, grade1=0, grade2=200):
        self.grade1 = grade1
        self.grade2 = grade2
        self.raw_data = tj.Files().all_data

    def get_data(self, *args, **kw):
        datas = self.raw_data
        fin_list = []
        for data in datas:
            flag = 1
            if data['年级'] >= self.grade1 and data['年级'] <= self.grade2:
                for arg in args:
                    if arg not in data.keys():
                        flag = 0
                for k, v in kw.items():
                    if k in data.keys():
                        if data[k] != v:
                            flag = 0
                    else:
                        flag = 0
            else:
                flag = 0
            if flag == 1:
                fin_list.append(data)
        return fin_list


class CiLeiHuoYong(BaseSearch):
    def __init__(self, grade1=0, grade2=200):
        super().__init__(grade1, grade2)
        self.data = super().get_data('用法', type='u')
        self.cileihuoyong = self.fin_data()

    def fin_data(self):
        fin_list = []
        for ch in self.data:
            if ch['用法'].find('→') > -1:
                fin_list.append(ch)
        return fin_list



class XuCi(BaseSearch):
    def __init__(self, grade1=0, grade2=200):
        super().__init__(grade1, grade2)
        self.data = super().get_data(type='m')
        self.xuci = self.data



class JuShi(BaseSearch):
    def __init__(self, grade1=0, grade2=200, js=''):
        super().__init__(grade1, grade2)
        if js == '':
            self.data = super().get_data(type='s')
        else:
            self.data = super().get_data(type='s', 句式=js)
        self.jushi = self.data


b = BaseSearch()
c = b.get_data(用法='古今异义')
for ch in c:
    print(ch)
