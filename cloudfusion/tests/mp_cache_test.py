# -*- coding: utf-8 -*- 
'''
Created on 04.06.2011

@author: joe
'''
from cloudfusion.util.mp_cache import MPCache
import time
from nose.tools import *
import math
import sys

KEY1 = "KEY1𠀋"
KEY2 = "KEY2𠀋"
KEY3 = "KEY3𠀋"
VALUE1 = 42
VALUE2 = 43
VALUE3 = 52
VALUE4 = "𠀋"

def test_refresh():
    test_obj = MPCache(1)
    test_obj.refresh(KEY1, VALUE2, time.time())
    test_obj.refresh(KEY1,VALUE1, time.time())
    assert test_obj.get_value(KEY1) == VALUE1
    test_obj.refresh(KEY1,VALUE2, time.time()-1000)
    assert test_obj.get_value(KEY1) == VALUE1, "Refresh should not have worked since the modified time of the 'disk' entry is older than the cache entry."
    assert not test_obj.is_dirty(KEY1)

def test_is_expired():
    test_obj = MPCache(1)
    test_obj.write(KEY1, VALUE1)
    time.sleep(2)
    assert test_obj.is_expired(KEY1)
       
def test_update():
    test_obj = MPCache(1)
    test_obj.write(KEY1, VALUE1)
    time.sleep(2)
    assert test_obj.is_expired(KEY1)
    test_obj.update(KEY1)
    assert not test_obj.is_expired(KEY1)
    
def test_write():
    test_obj = MPCache(1)
    test_obj.write(KEY1, VALUE1)
    test_obj.write(VALUE1, KEY1)
    assert test_obj.get_value(KEY1) == VALUE1
    assert test_obj.get_value(VALUE1) == KEY1
    assert test_obj.is_dirty(KEY1)
    
def test_get_keys():
    test_obj = MPCache(1)
    test_obj.refresh(KEY1, VALUE2, time.time())
    test_obj.write(KEY2, VALUE1)
    assert KEY1 in test_obj.get_keys()
    assert KEY2 in test_obj.get_keys()
    assert not KEY3 in test_obj.get_keys()
    
def test_get_value():
    test_obj = MPCache(1)
    test_obj.refresh(KEY1, VALUE2, time.time())
    assert test_obj.get_value(KEY1) == VALUE2
    test_obj.write(KEY1, VALUE1)
    assert test_obj.get_value(KEY1) == VALUE1
    
def test_get_modified():
    test_obj = MPCache(1)
    modified_time = time.time()
    test_obj.refresh(KEY1, VALUE2, modified_time)
    assert test_obj.get_modified(KEY1) == modified_time
    test_obj.write(KEY1, VALUE1)
    assert test_obj.get_modified(KEY1) <= time.time()
    
def test_set_modified():
    test_obj = MPCache(1)
    modified_time = 42
    before_modification = time.time()
    test_obj.write(KEY1, VALUE3)
    assert test_obj.get_modified(KEY1) <= time.time()
    assert test_obj.get_modified(KEY1) > before_modification
    test_obj.set_modified(KEY1, modified_time)
    assert test_obj.get_modified(KEY1) == modified_time
    
def test_get_size_of_dirty_data():
    test_obj = MPCache(1)
    assert test_obj.get_size_of_dirty_data() == 0
    test_obj.refresh(KEY1, VALUE4,  time.time())
    assert test_obj.get_size_of_dirty_data() == 0
    test_obj.write(KEY2, VALUE1)
    assert test_obj.get_size_of_dirty_data() == sys.getsizeof(VALUE1)
    test_obj.write(KEY2, VALUE3)
    assert test_obj.get_size_of_dirty_data() == sys.getsizeof(VALUE3)
    test_obj.write(KEY1, VALUE4)
    assert test_obj.get_size_of_dirty_data() == sys.getsizeof(VALUE3)+sys.getsizeof(VALUE4)
    test_obj.refresh(KEY2, VALUE1, time.time())
    assert test_obj.get_size_of_dirty_data() == sys.getsizeof(VALUE4)
    
def test_get_size_of_cached_data():
    test_obj = MPCache(1)
    modified_time = time.time()
    assert test_obj.get_size_of_cached_data() == 0
    test_obj.refresh(KEY1, VALUE4, modified_time)
    assert test_obj.get_size_of_cached_data() == sys.getsizeof(VALUE4)
    test_obj.write(KEY2, VALUE1)
    assert test_obj.get_size_of_cached_data() == sys.getsizeof(VALUE1)+sys.getsizeof(VALUE4)
    test_obj.write(KEY2, VALUE3)
    assert test_obj.get_size_of_cached_data() == sys.getsizeof(VALUE3)+sys.getsizeof(VALUE4)
    test_obj.refresh(KEY1, VALUE4, modified_time)
    assert test_obj.get_size_of_cached_data() == sys.getsizeof(VALUE3)+sys.getsizeof(VALUE4)
    
def test_is_dirty():
    test_obj = MPCache(1)
    test_obj.refresh(KEY1, VALUE2, time.time())
    assert not test_obj.is_dirty(KEY1)
    test_obj.write(KEY1, 42)
    assert test_obj.is_dirty(KEY1)

def test_exists():
    test_obj = MPCache(1)
    assert not test_obj.exists(KEY1)
    test_obj.write(KEY1, VALUE1)
    assert test_obj.exists(KEY1)
    assert not test_obj.exists(KEY2)
    
def test_delete():
    test_obj = MPCache(1)
    test_obj.write(KEY1, VALUE1)
    test_obj.write(VALUE1, KEY1)
    test_obj.delete(KEY1)
    test_obj.delete(KEY2)
    test_obj.delete(VALUE1)
    assert_raises( KeyError, test_obj.get_value, (VALUE1) )
    assert_raises( KeyError, test_obj.get_value, (KEY1) )
    assert not test_obj.exists(VALUE1)
    assert not test_obj.exists(KEY1)
    
