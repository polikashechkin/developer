import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    domino_lib = '/DOMINO/products/domino/11.7.0/python/domino'
    common_lib = '/DOMINO/products/_system/python/domino'
    for module in os.listdir(domino_lib):
        domino_module = os.path.join(domino_lib, module)
        if os.path.isfile(domino_module):
            print(module)
            common_module = os.path.join(common_lib, module)
            if os.path.isfile(common_module):
                os.remove(common_module)
            os.link(domino_module, common_module)

