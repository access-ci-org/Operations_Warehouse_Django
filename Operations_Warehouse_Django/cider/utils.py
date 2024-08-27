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
        org = org_list[i]
        org_scores = [ org[k] is not None for k in keys ]
        scores[i] = sum( org_scores )
    best = scores.index( max( scores ) )
    return org_list[ best ]


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
        'gpu_description',
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
        # 'xsede_services_only',
        'xsedenet_participant',
    ]
    return resource_attr_names


def mk_headers( cols, resources ):
    ''' Convert resources dict into html header data
    '''
    headers = [ '' ]
    for resource_id in cols[1:]:
        resource = resources[ resource_id ]
        resource_url = resource[ 'public_url' ]
        resource_short_name = resource[ 'short_name' ]
        org_url = resource[ 'organization_url' ]
        org_name = resource[ 'organization_name' ]
        logo_url = resource[ 'organization_logo_url' ]
        abbr = resource[ 'organization_abbreviation' ]
        img_size=75
        h = (
            f'<!-- org_abbr: {abbr} -->'
            f'<img width="{img_size}" height="{img_size}" src="{logo_url}" alt="{org_name}">'
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


def mk_html_table( data ):
    ''' convert features to table with
        resources along the top and
        features down the first column
    '''
    features = data[ 'attributes' ]
    resources = data[ 'resources' ]
    resource_ids = resource_ids_sorted_by( 'organization_abbreviation', resources )
    table = []
    f_names = sorted( get_resource_attribute_names() )
    for f in f_names:
        row = [f]
        for r in resource_ids:
            row.append( features[f][r] )
        table.append( row )
    cols = [ 'Attribute' ] + resource_ids
    headers = mk_headers( cols, resources )
    return { 'headers':headers, 'table':table }


def cider_to_coco( objects ):
    # objects is the data returned by the cider filter in django
    resources = {}
    features = {}
    for result in objects[ 'results' ]:
        attrs = result[ 'other_attributes' ]
        # add resource details
        resource_id = attrs[ 'compute_resource_id' ]
        resources[ resource_id ] = get_resource_info( attrs )
        # add feature data for this resource to the pivot table
        for k,v in attrs.items():
            try:
                features[k][resource_id] = v
            except KeyError as e:
                features[k] = { 'Attribute': k, resource_id: v }
    data = { 'resources': resources, 'attributes': features }
    return data


if __name__ == '__main__':
    raise UserWarning( 'not directly runnable' )
