from .documents import ResourceV4Index

class ResourceV4Process():
    def index(self, relations=None):
        newRels = []
        if relations:
            for i in relations:
                newRels.append({'RelatedID': i, 'RelationType': relations[i]})
        obj = ResourceV4Index(
                meta = {'id': self.ID},
                ID = self.ID,
                Affiliation = self.Affiliation,
                LocalID = self.LocalID,
                QualityLevel = self.QualityLevel,
                Name = self.Name,
                ResourceGroup = self.ResourceGroup,
                Type = self.Type,
                ShortDescription = self.ShortDescription,
                ProviderID = self.ProviderID,
                Description = self.Description,
                Topics = self.Topics,
                Keywords = self.Keywords,
                Audience = self.Audience,
                Relations = newRels,
                StartDateTime = self.StartDateTime,
                EndDateTime = self.EndDateTime
            )
        obj.save()
        return obj.to_dict(include_meta = True)

    def delete(self):
        obj = ResourceV4Index.get(self.ID).delete()
        return
