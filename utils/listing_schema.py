import hashlib,json

class Listings:

    #to dump all data coming from different sites to get a consistent database
    def __init__(self,title,company,source,skills,deadline,url):
        self.title = title
        self.company = company
        self.source = source
        self.skills = skills
        self.deadline = deadline
        self.url = url
        self.hash = self.generate_hash()
    
    #to prevent duplicates in database - hash job title with company
    def generate_hash(self):
        fingerprint = f"{self.title.lower().strip()}{self.company.lower().strip()}"
        return hashlib.sha256(fingerprint.encode()).hexdigest()
    
    #to convert into python dict
    def to_dict(self):
        return{
            "title" : self.title,
            "company" : self.company,
            "source" : self.source,
            "skills" : self.skills,
            "deadline" : self.deadline,
            "url" : self.url,
            "hash" : self.hash
            }
    
listing = Listings("Python Intern", "Systems Limited", "rozee.pk", ["Python", "Django"], "2025-08-01", "rozee.pk/job/123")
with open("test_listings.json","w") as response:
    json.dump(listing.to_dict(),response,indent = 4)


    
    
    


