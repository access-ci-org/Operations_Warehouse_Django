import tabulate
import json
import pathlib
import pprint

def put_html( data, filename ):
    ''' write data to a file
        prefixed with HTML opening tags and
        suffixed with valid HTML closing tags
    '''
    HTML_START='''
    <!DOCTYPE html>

    <html>
    <head>
    <style>
    table, td, th {
      border: 1px solid;
    }

    table {
      width: 100%;
      border-collapse: collapse;
    }
    </style>
    </head>
    <body>
    '''

    HTML_END='''
    </body>
    </html>
    '''
    outfile = pathlib.Path( filename )
    outfile.write_text( f"{HTML_START}<div>{table}</div>{HTML_END}" )


def get_json( filename ):
    ''' get json from a file '''
    infile = pathlib.Path( filename )
    with infile.open() as f:
        data = json.load( f )
    return data


def put_json( data, filename ):
    ''' write data as json to a file '''
    outfile = pathlib.Path( filename )
    with outfile.open( mode='w' ) as f:
        json.dump( data, f )

def get_best_org_details( org_list ):
    ''' find org with the largest quantity of non-null fields '''
    keys = [
        'organization_name',
        'organization_url',
        'organization_abbreviation',
        'organization_logo_url',
        'organization_id',
    ]
    scores = [0] * len(org_list)
    for i in range( len(org_list) ):
        # print( f"\t({org['organization_abbreviation']})" )
        org = org_list[i]
        org_scores = [ org[k] is not None for k in keys ]
        # pprint.pprint( org_scores )
        scores[i] = sum( org_scores )
        # scores[i] = sum( [ int(b) for b in org_scores ] )
        # for k in keys:
        #     print( f"\t\t{k}: {org[k]}" )
    # print( f"\t{scores}" )
    best = scores.index( max( scores ) )
    # print( f"\t\tindex of best: {best}" )
    return org_list[ best ]


# def get_institution_info( attrs ):
#     ''' INPUT cider other_attributes dict
#         OUTPUT dict with org info (as returned from cider)
#             organization_name
#             organization_url
#             organization_abbreviation
#             organization_logo_url   "https://cider.access-ci.…ource_providers/369/logo"
#             ...
#     '''
#     return get_best_org_details( attrs['organizations'] )


def get_resource_info( attrs ):
    ''' INPUT cider other_attributes dict
        OUTPUT dict with org info, keys:
            platform_name   " Indiana Jetstream2 GPU"
            public_url  "https://cider.access-ci.…lic/resources/RDR_000904"
            resource_descriptive_name   "Indiana Jetstream2 GPU"
            short_name  "Jetstream2 GPU"
            +++++++ PLUS ORG INFO +++++++
            city    "Bloomington"
            state   "IN"
            country "US"
            organization_id 561
            organization_url    "https://pti.iu.edu/"
            organization_code   "0087312"
            organization_name   "Indiana University"
            organization_logo_url   "https://cider.access-ci.…ource_providers/369/logo"
            external_organization_id    "grid.257410.5"
            organization_abbreviation   "Indiana U"
            external_organization_id_type   "GRID"
    '''
    keys = [
        'compute_resource_id',
        'platform_name',
        'public_url',
        'resource_descriptive_name',
        'short_name',
    ]
    resource_info = { k: attrs[k] for k in keys }
    resource_info.update( get_best_org_details( attrs['organizations'] ) )
    return resource_info


def get_resource_attribute_names():
    resource_attr_names = [
        # access_description,
        'advance_max_reservable_su',
        'advance_reservation_support',
        # allocations_info,
        # alternate_login_hostname,
        'batch_system',
        'community_software_area',
        # community_software_area_email,
        # community_software_area_feature_user_description,
        # compute_resource_id,
        'cpu_count_per_node',
        'cpu_speed_ghz',
        'cpu_type',
        'disk_size_tb',
        'display_in_xsede_su_calculator',
        # features,
        # gateway_recommended_use,
        # gpu_description,
        'graphics_card',
        'interconnect',
        # ip_address,
        'job_manager',
        # latitude,
        'local_storage_per_node_gb',
        # login_hostname,
        # longitude,
        'machine_type',
        'manufacturer',
        'max_reservable_su',
        'memory_per_cpu_gb',
        'model',
        'nfs_network',
        'nickname',
        'node_count',
        'operating_system',
        # organizations,
        'parallel_file_system',
        # parent_resource,
        'peak_teraflops',
        'platform_name',
        'primary_storage_shared_gb',
        # public_url,
        # recommended_use,
        # resource_descriptive_name,
        'resource_type',
        'rmax',
        'rpeak',
        # sensitive_data_support_description,
        # short_name,
        'storage_network',
        'supports_sensitive_data',
        # user_guide_url,
        'xsede_services_only',
        'xsedenet_participant',
    ]
    return resource_attr_names


def mk_html_table( data ):
    ''' convert features to html table with
        resources along the top and
        features down the first column
    '''
    features = data[ 'features' ]
    resources = data[ 'resources' ]
    resource_ids = resource_ids_sorted_by( 'organization_abbreviation', resources )
    table = []
    f_names = list( features.keys() )
    f_names.sort()
    for f in f_names:
        row = [f]
        for r in resource_ids:
            row.append( features[f][r] )
        table.append( row )
    cols = [ 'Feature' ] + resource_ids
    headers = mk_headers( cols, resources )
    return tabulate.tabulate( table, headers=headers, tablefmt='unsafehtml' )


def mk_headers( cols, resources ):
    ''' Convert resources dict into html header data
    '''
    headers = [ cols[0] ]
    for resource_id in cols[1:]:
        resource = resources[ resource_id ]
        resource_url = resource[ 'public_url' ]
        resource_short_name = resource[ 'short_name' ]
        org_url = resource[ 'organization_url' ]
        org_name = resource[ 'organization_name' ]
        logo_url = resource[ 'organization_logo_url' ]
        abbr = resource[ 'organization_abbreviation' ]
        h = (
            f'<!-- org_abbr: {abbr} -->'
            f'<img src="{logo_url}" alt="{org_name}">'
            '<br/>'
            f'<a href="{org_url}">({abbr})</a>'
            '<br/>'
            f'<a href="{resource_url}">{resource_short_name}</a>'
        )
        headers.append( h )
    return headers


def resource_ids_sorted_by( key, resources ):
    ''' return list of resource_ids sorted by "key" '''
    id_list = []
    key2id = {}
    for id in resources.keys():
        match_key = resources[id][key]
        if match_key in key2id:
            key2id[ match_key ].append( id )
        else:
            key2id[ match_key ] = [ id ]
    for key in sorted( key2id.keys() ):
        id_list.extend( key2id[ key ] )
    return id_list


if __name__ == "__main__":
    # objects is the data returned by the cider filter in django
    objects = get_json( filename='raw_coco_data.json' )
    #keys_lvl1 = [ k for k in objects.keys() ]
    # ['results',      #array
    #  'status_code'   #int
    # ]
    resources = {}
    features = {}
    for result in objects[ 'results' ]:
        # result = { cider_type: "compute",
        #            other_attributes: dict(...)
        #          }
        attrs = result[ 'other_attributes' ]

        # add resource details
        resource_id = attrs[ 'compute_resource_id' ]
        resources[ resource_id ] = get_resource_info( attrs )
        # add feature data for this resource to the pivot table
        for k in get_resource_attribute_names():
            v = attrs[k]
            try:
                features[k][resource_id] = v
            except KeyError as e:
                features[k] = { 'Feature': k, resource_id: v }
    data = { 'resources': resources, 'features': features }
    put_json( data=data, filename='features.json' )


    table = mk_html_table( data )
    put_html( data=table, filename='features.html' )
