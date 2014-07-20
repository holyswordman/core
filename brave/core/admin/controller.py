# encoding: utf-8

from __future__ import unicode_literals

from datetime import datetime

from web.core import Controller, HTTPMethod, request
from web.core.locale import _
from web.core.http import HTTPFound, HTTPNotFound

from brave.core.character.model import EVECharacter, EVECorporation, EVEAlliance
from brave.core.group.model import Group
from brave.core.group.acl import ACLList
from brave.core.util.predicate import authorize, is_administrator
from brave.core.key.model import EVECredential
from brave.core.account.model import User


class SearchCharInterface(HTTPMethod):
    """Handles /admin/search/char"""

    def get(self, character=None, charMethod=None, alliance=None, corporation=None, group=None, banned=None, submit=None):
        
        # Have to be an admin to access admin pages.
        if not is_administrator:
            raise HTTPNotFound()

        if not submit:
            return 'brave.core.admin.template.searchChar', dict(area='admin')

        
        # Seed the initial results.
        chars = EVECharacter.objects()
            
        # Go through and check all of the possible posted values
        
        # Limit chars to the character name entered.
        if character:
            if charMethod == 'contains':
                chars = chars.filter(name__icontains=character)
            elif charMethod == 'starts':
                chars = chars.filter(name__istartswith=character)
            elif charMethod == 'is':
                chars = chars.filter(name__iexact=character)
            else:
                return 'json:', dict(success=False, message=_("You broke the web page. Good Job."))
        
        # Limit to characters in the specified alliance.
        if alliance:
            alliance = EVEAlliance.objects(name=alliance).first()
            chars = chars.filter(alliance=alliance)
        
        # Limit to characters in the specified corporation.
        if corporation:
            corporation = EVECorporation.objects(name=corporation).first()
            chars = chars.filter(corporation=corporation)
        
        # Limit to characters in the specified group.
        if group:
            groupList = []
            for c in chars:
                if group in c.tags:
                    groupList.append(c.id)
                    
            chars = chars.filter(id__in=groupList)
            
        # Limit to characters with the specified banned status.
        if banned:
            charList = []
            if banned.lower() == 'true':
                for c in chars:
                    if c.banned:
                        charList.append(c.id)
            elif banned.lower() == 'account':
                for c in chars:
                    if c.owner.banned:
                        charList.append(c.id)
            else:
                for c in chars:
                    if not c.banned and not c.owner.banned:
                        charList.append(c.id)
                        
            chars = chars.filter(id__in=charList)
            
        return 'brave.core.admin.template.searchChar', dict(area='admin', result=chars, success=True)


class SearchKeyInterface(HTTPMethod):
    """Handles /admin/search/key"""
    def get(self, keyID=None, keyMask=None, violation=None, submit=None):
        
        # Have to be an admin to access admin pages.            
        if not is_administrator:
            raise HTTPNotFound()

        if not submit:
            return 'brave.core.admin.template.searchKey', dict(area='admin')
        
        # Seed the initial results.
        keys = EVECredential.objects()
        
        # Limit to keys with the specified ID.
        if keyID:
            keys = keys.filter(key=keyID)
        
        # Limit to keys with the specified Mask.
        if keyMask:
            keys = keys.filter(_mask=keyMask)
            
        # Limit to keys with the specified violation.
        if violation.lower() == "none":
            keys = keys.filter(violation=None)
        elif violation:
            keys = keys.filter(violation__iexact=violation)
            
        return 'brave.core.admin.template.searchKey', dict(area='admin', result=keys, success=True)
        
        
class SearchUserInterface(HTTPMethod):
    """Handles /admin/search/user"""
    def get(self, username=None, userMethod=None, ip=None, duplicate=None, banned=None, submit=None):
        
        # Have to be an admin to access admin pages.
        if not is_administrator:
            raise HTTPNotFound()

        if not submit:
            return 'brave.core.admin.template.searchUser', dict(area='admin')
            
        # Seed the initial results.
        users = User.objects()
        
        # Limit to users with the specified username.
        if username:
            if userMethod == 'contains':
                users = users.filter(username__icontains=username)
            elif userMethod == 'starts':
                users = users.filter(username__istartswith=username)
            elif userMethod == 'is':
                users = users.filter(username__iexact=username)
            else:
                return 'json:', dict(success=False, message=_("You broke the web page. Good Job."))
        
        # Limit to users with the specified IP address.
        if ip:
            users = users.filter(host=ip)
            
        # Limit to users with the specified duplicate status
        if duplicate.lower() == "ip":
            users = users.filter(other_accs_IP__exists=True)
        elif duplicate.lower() == "char":
            users = users.filter(other_accs_char_key__exists=True)
            
        # Limit to users with the specified banned status.
        if banned:
            banList = []
            for u in users:
                if u.banned:
                    banList.append(u.id)
            
            if banned.lower() == 'true':
                users = users.filter(id__in=banList)
            else:
                users = users.filter(id__nin=banList)
            
        return 'brave.core.admin.template.searchUser', dict(area='admin', result=users, success=True)
        
        
class SearchController(Controller):
    char = SearchCharInterface()
    key = SearchKeyInterface()
    user = SearchUserInterface()
    
    
class AdminController(Controller):
    """Entry point for the Search RESTful interface."""

    search = SearchController()

    def index(self):
        return 'brave.core.admin.template.search', dict(area='admin')
