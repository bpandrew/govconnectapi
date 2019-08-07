
var myTable;

function BuildTable(table_name, timeout, base_url, rows, _orderby, _filter) {

	// Set timeout to 0 to have no caching
	//_orderby = 1

	// Set the names for the localStorage variables
	_cache_time = base_url+"supplier_cache_time" // Stores the last time the page was cached
	_page = base_url+"page" // Stores the last page number loaded,  in case we are interupted mid download of the dataset
	_cached_data = base_url+"data" // Stores the data for this particular page

	myTable = $("#"+table_name).DataTable({
		"orderCellsTop": true,
        "fixedHeader": true,
		"paging": true,
		"lengthChange": true,
		"searching": true,
		"ordering": true,
		"info": true,
		"order": [
			[_orderby, "asc"]
		]
	});

	// Check if the filter boxes should be placed above the columns
	if (_filter === true) {
		// Setup - add a text input to each footer cell
		$("#"+table_name+" thead tr").clone(true).appendTo("#"+table_name+" thead");
		$("#"+table_name+" thead tr:eq(1) th").each(function(i) {
			var title = $(this).text();
			$(this).html('<input type="text" size="14" placeholder="Filter ' + title + '" />');

			$('input', this).on('keyup change', function() {
				if (myTable.column(i).search() !== this.value) {
					myTable
						.column(i)
						.search(this.value)
						.draw();
				}
			});
		});
	}

	cache_timeout = timeout * 1000 * 60 // set the timeout in milliseconds

	// if local cache has not been set, or not all the pages were loaded last time..
	if ( (localStorage.getItem(_cache_time) === null) || (localStorage.getItem(_cache_time) < Date.now()-cache_timeout )) {
		localStorage.setItem(_cache_time, Date.now());
		localStorage.setItem(_page, 1);
		localStorage.setItem(_cached_data, JSON.stringify({"data":[]}));
	} 

	$.ajax({
		type: "POST",
		url: "/"+ base_url +"?page=1",
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		success: function (response) {
			//var jsonObject = JSON.parse(response.data);
			var totalPages = response.pages;
			// If there is still pages to cache
			if ( (localStorage.getItem(_page)<=totalPages) || (cache_timeout<1) ){
				$("#data_source").html("Cloud Data");
				console.log("Fetching new data");
				for (i = 0; i < totalPages; i++) {
					PopulateItemsTable(base_url, rows, _page, _cached_data);
					page = localStorage.getItem(_page);
					page++
					localStorage.setItem(_page, page);
				}
				//$("div#loading_table").hide();
			} else {
				$("#data_source").html("Cached Data");
				console.log("Using cached data");
				cached_data = JSON.parse(localStorage.getItem(_cached_data));
				cached_data = cached_data.data
				table_data = []
				var i;
				for (i = 0; i < cached_data.length; i++) { 
					push_data = []
					for (j = 0; j < rows.length; j++) {
						push_data.push(cached_data[i][rows[j]] )
					}
					table_data.push(push_data)
					//table_data.push( [ cached_data[i]['link'], cached_data[i]['abn'] ] )
				}
				myTable.rows.add(table_data)
				myTable.draw();
				//$("div#loading_table").hide();
			}
			
		},
		complete: function (response) {
			$("div#loading_table").hide();
		}
	});
};


function PopulateItemsTable(base_url, rows, _page, _cached_data) {
	$.ajax({
		type: "POST",
		url: "/"+ base_url +"?page="+localStorage.getItem(_page),
		contentType: "application/json; charset=utf-8",
		dataType: "json",
		success: function (response) {
		//var jsonObject = JSON.parse(response.data);
		var totalPages = response.pages;
		var jsonObject = response.data;
		existing_storage = JSON.parse(localStorage.getItem(_cached_data));
		
		//alert(existing_storage.data);
		//alert(jsonObject.length);
		index = 0;
		while (index < jsonObject.length) { 
			existing_storage['data'].push(jsonObject[index]);
			index++;
		}

		localStorage.setItem(_cached_data, JSON.stringify(existing_storage));
		//alert(localStorage.getItem(_cached_data));
		var result = jsonObject.map(function(item){
			var result = [];
			for (i = 0; i < rows.length; i++) {
				result.push(item[rows[i]]); 
				//console.log(item[rows[i]]);
			}
			//result.push(item.link); 
			//result.push(item.abn); 
			// .... add all the values required
			return result;
		});
		//console.log(result);
		myTable.rows.add(result); // add to DataTable instance
		myTable.draw(); // always redraw
		}
	});
}
