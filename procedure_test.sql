-- use relationdb;
use dbtest;

drop procedure if exists pro_test;\

DELIMITER $$
create procedure pro_test ( 
	test varchar(10)
    )
    begin

        drop table if exists tmp_table;
        create temporary table tmp_table select * from test_table;
        -- select count(*) from tmp_table;
        
        -- insert machine
        -- insert into machine select null, machine_name as m_name, test as facility_name , resolution_x ,resolution_y, insp_light_r, insp_light_g,insp_light_b,insp_light_pad,insp_light_axs
        insert into machine select null, tmp.machine_name as m_name, test as facility_name , tmp.resolution_x ,tmp.resolution_y
        from tmp_table as tmp where not exists(select m_name from machine where m_name = tmp.machine_name ) LIMIT 1;        
        -- set @test = (select id from machine where exists(select m_name from machine as m join tmp_table as tmp on tmp.machine_name = m.m_name) and );
                
        -- set @machine_id = last_insert_id();
		-- set @tmp_var :=null;
        set @machine_id :=null;
        select m.id into @machine_id from machine as m join tmp_table as tmp on m.m_name = tmp.machine_name limit 1;
        -- set @machine_id = (select if(@machine_id,@machine_id, @tmp_var) limit 1) ;		        
                            
        -- insert vision rcp
        insert into vision_recipe select null, @machine_id, tmp.recipe_name  from tmp_table as tmp where not exists (select rcp_name from vision_recipe where rcp_name = tmp.recipe_name ) LIMIT 1;                
        set @vrcp_id :=null;
        select vrcp.id into @vrcp_id from vision_recipe as vrcp join tmp_table as tmp on vrcp.rcp_name = tmp.recipe_name limit 1;
        -- set @vrcp_id = (select if(@vrcp_id,@vrcp_id,@tmp_var) limit 1);                
        
        set foreign_key_checks=0;
        
        -- insert lot info 
        insert into lot_information(product_id,recipes_id,machine_id) 
        select tmp.product_id , @vrcp_id, @machine_id from tmp_table as tmp 
        where not exists (select * from lot_information as lot_info 
        join machine as m on m.id = lot_info.machine_id 
        where lot_info.product_id = tmp.product_id
        and tmp.machine_name= m.m_name ) limit 1;
		
        set @lot_id :=null;
        select lot_info.id into @lot_id from 
        (lot_information as lot_info join machine as m on m.id = lot_info.machine_id) 
        join tmp_table as tmp on lot_info.product_id = tmp.product_id 
        and m.m_name = tmp.machine_name limit 1;
		
        -- select * from lot_information where id = @lot_id;
        
        -- insert bundle
        insert into bundle (sorter_no,cycle_no,lot_information_id) 
        select tmp.sorter_no,tmp.cycle_no, @lot_id from tmp_table as tmp 
        where not exists (select * from bundle as bd 
        join lot_information as lot_info on bd.lot_information_id = lot_info.id
        where bd.sorter_no = tmp.sorter_no
        and bd.cycle_no = tmp.cycle_no
        and lot_info.product_id = tmp.product_id) limit 1;
        
        set @bundle_id :=null;
        select bd.id into @bundle_id from 
        (bundle as bd join lot_information as lot_info on bd.lot_information_id = lot_info.id) 
        join tmp_table as tmp on lot_info.product_id = tmp.product_id 
        and bd.sorter_no = tmp.sorter_no and bd.cycle_no = tmp.cycle_no limit 1;
        
        -- select * from bundle where id = @bundle_id;
     
		
		-- insert strips
        insert into strips
        select tmp.barcode,tmp.strip_no, @bundle_id, tmp.insp_start,tmp.insp_end
        from tmp_table as tmp
        where not exists (select * from strips
        join bundle as bd on strips.bundle_id = bd.id
        where strips.strip_no = tmp.strip_no 
        and bd.sorter_no = tmp.sorter_no 
        and bd.cycle_no = tmp.cycle_no) limit 1; 
        
		set @barcode_num :=null;
        select strips.barcode into @barcode_num
        from (strips join bundle as bd on bd.id = strips.bundle_id)
        join tmp_table as tmp on bd.sorter_no = tmp.sorter_no 
        and bd.cycle_no = tmp.cycle_no 
        and strips.barcode = tmp.barcode limit 1;               


        -- insert defect code                
        insert into defect_code (recipes_id, defect_code, detect_light_r,detect_light_g,detect_light_b,detect_light_pad,detect_light_axs,detect_light_h,detect_light_i,detect_light_s, insp_light_r, insp_light_g,insp_light_b,insp_light_pad,insp_light_axs)
        select @vrcp_id, tmp.defect_code, tmp.detect_light_r,tmp.detect_light_g,tmp.detect_light_b,tmp.detect_light_pad,tmp.detect_light_axs,tmp.detect_light_h,tmp.detect_light_i,tmp.detect_light_s, insp_light_r, insp_light_g,insp_light_b,insp_light_pad,insp_light_axs
        from tmp_table as tmp 
        where not exists (select * from defect_code as dc
        join vision_recipe as vrcp on dc.recipes_id = vrcp.id
        where vrcp.rcp_name = tmp.recipe_name
        and dc.defect_code = tmp.defect_code)
        group by tmp.defect_code;
        
        
        
		-- insert into defect_code (recipes_id, defect_code, detect_light_r,detect_light_g,detect_light_b,detect_light_pad,detect_light_axs,detect_light_h,detect_light_i,detect_light_s, insp_light_r, insp_light_g,insp_light_b,insp_light_pad,insp_light_axs)
-- 		select @vrcp_id, tmp.defect_code, tmp.detect_light_r,tmp.detect_light_g,tmp.detect_light_b,tmp.detect_light_pad,tmp.detect_light_axs,tmp.detect_light_h,tmp.detect_light_i,tmp.detect_light_s, insp_light_r, insp_light_g,insp_light_b,insp_light_pad,insp_light_axs
-- 		from tmp_table as tmp
-- 		where not exists (select * from defect_code as dc 
-- 		join vision_recipe as vrcp on dc.recipes_id = vrcp.id
-- 		where vrcp.rcp_name = tmp.recipe_name 
-- 		and dc.defect_code = tmp.defect_code) group by defect_code;
	
        -- set @dcode_id :=null;
--         select dc.id into @dcode_id 
--         from (defect_code as dc 
--         join vision_recipe as vrcp 
--         on dc.recipes_id = vrcp.id)
--         join tmp_table as tmp on vrcp.id = tmp.
	
		-- insert vrs operator
        insert into operator 
        select null, tmp.vrs_operator from tmp_table as tmp
        where not exists (select * from operator) group by ifnull(tmp.vrs_operator,0) ;
    
		-- insert vrs dcode
        
    
    
		-- insert vrs
        -- insert into VRS
        
        
    
    
		-- insert ADC
--         insert into ADC (ai_final_bin, ai_good, ai_defect, ai_recipe, vrs_id)
        
        
        
        
    
		-- insert points
        -- insert into points
--         select null,tmp.defect_index,tmp.unit_x, tmp.unit_y,tmp.pos_x,tmp.pos_y, dc.defect_code , 0, tmp.defect_size, tmp.defect_len, tmp.defect_width, tmp.defect_height, @barcode_num
--         from tmp_table as tmp
--         where not exists (select * from points 
--         
        
		

        
        set foreign_key_checks=1;
		
        
        
        
        
	end $$
DELIMITER ;

-- call pro_test('test');

    
	
    