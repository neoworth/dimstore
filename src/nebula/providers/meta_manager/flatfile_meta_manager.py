"""
"  default flat file meta data manager, keep records of all features in store
"""
import os
import pickle as pl
from nebula.core.metadata_keys import MetadataKeys
from nebula.providers.meta_manager.meta_manager_base import MetaManagerBase
from nebula.utility.file_functions import file_exist, read_binary_file, write_binary_file


class FlatFileMetaManager(MetaManagerBase):

    def __init__(self, config):
        self.config = config
        self.path = "%s/%s"%(config['root_dir'], config['folder_name'])
        self.filename = self.config['file_name']

    def register(self, feature):
        # handle edge case
        self.__apply_default_namespace__(feature)
        if not self.__check_feature_name_uniqueness__(feature):
            print("> Feature name: '%s' is not unique in namespace: %s" % (feature.name, feature.namespace))
            return
        # get catalog object and register feature
        uid = str(feature.uid)
        namespace = feature.namespace
        catalog = self.__get_catalog__(namespace = namespace)
        catalog[uid] = feature
        # write back catalog
        self.__save_catalog__(catalog, namespace = namespace)


    """
    "
    " read feature meta data by given namespace
    "
    """
    def read(self, namespace='default', match_child=True, **kwargs):
        """
        @param::namespace: the namespace in string
        @param::match_child: boolean value indicate whether match sub namespaces
        @param::kwargs: the keyword parameter list
        return a dictionary of {uid:feature meta data}
        """
        feature_dict = {}
        if file_exist(self.path, self.filename):
            bytes_obj = read_binary_file(self.path, self.filename)
            catalog = pl.loads(bytes_obj)
            canonical_ns = self.__build_canonical_namespace__(namespace)
            if match_child:
                for key_ns in catalog:
                    if self.__namespace_match__(canonical_ns, key_ns):
                        feature_dict.update(catalog[key_ns])
            else:
                if canonical_ns in catalog:
                    feature_dict = catalog[canonical_ns]
        return feature_dict

    """
    "
    " get all namespaces in feature store
    "
    """
    def namespaces(self, **kwargs):
        """
        @param::kwargs: keyword parameter list
        return list of canonical namespace objects and the counts of features in that namespace
        """
        catalog = {}
        if file_exist(self.path, self.filename):
            # read and deserialize catalog object
            bytes_obj = read_binary_file(self.path, self.filename)
            catalog = pl.loads(bytes_obj)
        return catalog.keys(),list(map(len,catalog.values()))

    """
    "
    " remove features in the given FeatureSet instance
    "
    """
    def remove(self, feature_set, **kwargs):
        """
        @param::feature_set: the instance of FeatureSet class
        @param::kwargs: keyword parameter list
        return none
        """
        pass

    """
    "
    " update features in the given FeatureSet instance
    "
    """
    def update(self, feature_set, **kwargs):
        """
        @param::feature_set: the instance of FeatureSet class
        @param::kwargs: keyword parameter list
        return none
        """
        pass
    

    """
    "
    " implementation of base class method.
    " operation takes O(N), where N is the max of number of features in any namespace.
    "
    """
    def __check_feature_name_uniqueness__(self, feature):
        """
        @param::feature: the feature metadata object.
        return boolean value of uniqueness of feature name in given namespace.
        """
        if file_exist(self.path, self.filename):
            # read and deserialize catalog object
            bytes_obj = read_binary_file(self.path, self.filename)
            catalog = pl.loads(bytes_obj)
            # check uniquess
            feature_name = feature.name
            namespace = feature.namespace
            canonical_ns = self.__build_canonical_namespace__(namespace)
            if  canonical_ns in catalog:
                    for _,feature in catalog[canonical_ns].items():
                        if feature.name.lower() == feature_name.lower():
                            return False
        return True

    """
    "
    " read the catalog dumps and deserialize it 
    "
    """
    def __get_catalog__(self, namespace=None):
        """
        @param::namespace: the string namespace of catalog
        return the catalog object or None
        """
        catalog_rtn = {}
        namespace = self.__build_canonical_namespace__(namespace)
        if file_exist(self.path, self.filename):
            # read and deserialize catalog object
            bytes_obj = read_binary_file(self.path, self.filename)
            catalog = pl.loads(bytes_obj)
            if namespace in catalog:
                catalog_rtn = catalog[namespace]        
        return catalog_rtn

    """
    "
    " serialize the catalog and save it to flat file
    "
    """
    def __save_catalog__(self, sub_catalog, namespace=None):
        """
        @param::sub_catalog: the catelog object contains feature metadata
        @param::namespace: the string namespace of catalog
        return None
        """
        # check edge case
        if sub_catalog == None:
            raise Exception('> save_catalog: (sub)catalog can not be None!')
        if not isinstance(sub_catalog, dict):
            raise Exception('> save_catalog: (sub)catalog is not dictionary type!')
        # save (sub)catalog into flat file
        catalog = {}
        namespace = self.__build_canonical_namespace__(namespace)
        if file_exist(self.path, self.filename):
            bytes_obj = read_binary_file(self.path, self.filename)
            catalog = pl.loads(bytes_obj)
            catalog[namespace] = sub_catalog
        else:
            catalog[namespace] = sub_catalog
        dumps = pl.dumps(catalog)
        write_binary_file(self.path, self.filename, dumps)


    """
    "
    " method apply default namespace if given namespace is invalid
    " 
    """
    def __apply_default_namespace__(self, feature):
        """
        @param::feature: the instance of feature metadata class
        return none
        """
        if feature.namespace == None or feature.namespace.strip() == '':
            feature.namespace = 'default'


    """
    "
    " build a set of canonical namespaces optimized for query/filter operation
    " e.g., foo.bar.kai => {(foo,0),(bar,1),(kai,2)}
    " check whether or not namepace match take O(N), where N is the number of tuples in namespace.
    "
    """
    def __build_canonical_namespace__(self, namespace):
        """
        @param::namespace: string representation of namespace.
        return a set contains canonical namespace
        """
        canonical_ns = []
        existed_parts = set([])
        if namespace == None or namespace.strip() == '':
            canonical_ns.append((0,'default'))
        else:
            for index,part in enumerate(namespace.split('.')):
                if not part.isalnum():
                    raise Exception("> The namespace is invalid! Make sure the namespace contains alphanumeric and '.' symbol only.")
                if part.lower() in existed_parts:
                    raise Exception("> The namespace can not contains duplicated tuples!")
                else:
                    canonical_ns.append((index,part.lower()))
                    existed_parts.add(part.lower())

        return tuple(canonical_ns)

    """
    "
    " check if the canonical namespaces match. The match operation is not communicative.
    " e.g., a match b  !=> b match a
    " operation takes O(N), where N is the number of tuples in namespace
    "
    """
    def __namespace_match__(self,namespace1, namespace2):
        if namespace1 == None or namespace2 == None:
            return False
        for part in namespace1:
            if part not in namespace2:
                return False
        return True

                    






