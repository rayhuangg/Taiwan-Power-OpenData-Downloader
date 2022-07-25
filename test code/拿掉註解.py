#%%

txt = ["星崴光(註10)", "星崴光", "星崴光(註5)", "其它購電太陽能","馬祖珠山(註4)"]

for i in txt:
    # print(i)
    if "註" in i:
        print(i)
        print(i.index("註"))
        print(i[:i.index("註")-1])
