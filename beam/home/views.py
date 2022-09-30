from django.shortcuts import render
from django.views import generic


class HomeView(generic.base.TemplateView):
    template_name = "home/home.html"
    
    def get_session_data(self, **kwargs):
        return self.request.session
    
    def count_visits(self):
        session_data = self.get_session_data()
        return session_data.get('num_visits', 0)
         
    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        
        session_data = self.get_session_data()
        # num_visits = self.count_visits()
        num_visits = session_data.get('num_visits', 0)
        session_data['num_visits'] = num_visits + 1
        
        session_data_list = list()
        
        for key in session_data.keys():
            session_data_list.append(key)
        
        context["session_data_list"] = session_data_list
        context["num_visits"] = session_data['num_visits']
        
        return context

