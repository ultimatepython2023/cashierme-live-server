class Paginate:
    MODEL_NAME = ""

    def __init__(self, model_name):
        self.MODEL_NAME = model_name

    def get_current_rows_paginate(self, all_rows_count, limit, current_select) :
        ''' this function to return paginate with all
         rows count and get start and end rows and all pages count'''
        try :
            current_start_rows=0  # null variable for start rows
            current_end_rows=0  # null variable for end rows
            all_pages_count_var= self.get_count_pages_paginate(all_rows_count,limit)  # get all pages count by function
            if all_rows_count :  # check if data in all_rows_count
                current_end_rows=current_select*limit
                current_start_rows=current_end_rows-limit
                if current_end_rows>all_rows_count :
                    current_end_rows=all_rows_count
                print(current_start_rows, current_end_rows)

                return { "status" : "Success",
                         "current_start_rows" : current_start_rows,
                         "current_end_rows" : current_end_rows,
                         "all_pages_count" : all_pages_count_var }
        except Exception as Error :
            print(Error)
            return { "current_start_rows" : 0,
                     "current_end_rows" : 0,
                     "all_pages_count" : 0,
                     "error" : str(Error) }

    def get_count_pages_paginate(self, all_rows_count, limit) :
        '''get pages count by get_all_rows_count / limit if have float add 1+
         -- this work to check value if float add +1 in value
         -- if value is integer not add +1
         -- use is_integer() function to check value is integer
                 or not and return True or False '''
        try :
            rows_count=0
            all_rows_count_var=all_rows_count/limit
            get_rows_count=all_rows_count_var.is_integer()
            if not get_rows_count :
                rows_count=int((all_rows_count_var)+1)
                return rows_count
            else :
                rows_count=int(all_rows_count_var)
                return rows_count
        except Exception as Error :
            print(Error)
            return 0

    def get_pagination_for_list(self, my_list, page_no,
                                select_pagination_no) :
        get_list_len=len(my_list)
        buttons_no=get_list_len/select_pagination_no
        get_start_and_end_list=self.generate_pagination_start_end(page_no,
                                                             select_pagination_no)
        start=get_start_and_end_list[ 'start' ]
        end=get_start_and_end_list[ 'end' ]
        print(start, end)
        return { "list_paginate" : my_list[ start :end ],
                 "all_list_len" : get_list_len,
                 "button_no" : select_pagination_no }

    def generate_pagination_start_end(self, current_page, current_list) :
        if current_list<36 :
            if current_page == 1 :
                start=0
                end=current_list*current_page
                return { "start" : start, "end" : end }
            else :
                start=int((current_list*current_page)-current_list)
                end=(current_list*current_page)
                return { "start" : start, "end" : end }
