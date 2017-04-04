# PhotoShare-Web-App
The project uses Flask on Python which is a micro web framework written in Python along with MySQL database to implement a photo sharing website.

Description of use-cases: A user can have multiple friends and it is stored in the database as a self-relation to the users. A user can post comments on photos. Each comment must be posted by a user and associated with a single user, however a user can post multiple comments. Each Comment is associated with exactly one photo. A photo can have multiple comments. A photo has total participation in relationship with the users. Photos have a weak entity called tags which contain the names of all the tags associated with that photo. Two photos can have the same tag. A photo is always contained in an album. An album can have multiple photos. Similarly, A user can have multiple albums but an album must be associated to one or more users.